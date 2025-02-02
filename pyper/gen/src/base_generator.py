import concurrent.futures
import json
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List

import chromadb

from pyper.llm_api import make_llm_request


class BaseGenerator(ABC):
    def __init__(self):
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection("question")

    def _generate_question_task(
        self,
        syllabus,
        batch: int,
        knowledge: bool,
        max_tokens: int = 150,
    ):
        """Generate question by randomly selecting one syllabi from generated syllabus."""
        questions = []
        # Randomly select one syllabus
        syl = syllabus if knowledge else random.choice(syllabus)

        # Generate questions for each session in the selected syllabus
        for s in syl["syllabus"]:
            session = s["session_name"]
            concepts = s["key_concepts"]

            encode_message = self._build_question_prompt(
                session=session,
                concepts=concepts,
                batch=batch,
                max_tokens=max_tokens,
            )

            res = make_llm_request(
                messages=encode_message,
                response_format=self.question_schema,
                temperature=random.choice([0.6, 0.8, 1.0, 1.2]),
                frequency_penalty=random.choice([0.6, 0.8, 1.0, 1.2]),
            )
            questions.extend(res["questions"])

            print(res)
            print("")
        return questions

    def _process_single_answer(self, question: Dict, max_tokens: int = 150) -> Dict:
        q = question["question"]
        input = question["input"]

        encode_message = self._build_answer_prompt(
            question=q,
            input=input,
            max_tokens=max_tokens,
        )

        return make_llm_request(
            messages=encode_message,
            response_format=self.answer_schema,
        )

    def _generate_answers(self, question_tasks: List, max_tokens: int = 150):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # keep track of the order
            futures_dict = {
                executor.submit(self._process_single_answer, question, max_tokens): i
                for i, question in enumerate(question_tasks)
            }

            answers = [None] * len(question_tasks)

            # collect results as they complete and place in correct position
            for future in concurrent.futures.as_completed(futures_dict):
                original_index = futures_dict[future]
                try:
                    result = future.result()
                    answers[original_index] = result
                except Exception as e:
                    print(f"Error processing question at index {original_index}: {e}")
                    answers[original_index] = None
        return answers

    def _deduplicate_task(
        self,
        new_tasks: List,
    ):
        """
        Filter similar task by calculating similarity score of questions.
        """
        print("filtering similar questions...")
        clean_questions = []
        for i, q in enumerate(new_tasks):
            res = self.collection.query(query_texts=[q["question"]], n_results=1)
            if not res["distances"][0] or res["distances"][0][0] > 0.7:
                self.collection.add(
                    documents=[q["question"]], ids=[f"gen_{time.time()}"]
                )
                # add the entire task to the result set
                clean_questions.append(q)
        return clean_questions

    def save_results(self, questions: List, answers: List, output_path: str):
        """Common method to save results"""
        with open(output_path, "w") as f:
            for q, a in zip(questions, answers):
                d = {
                    "instruction": q["question"],
                    "input": q["input"],
                    "output": a["answer"],
                }
                f.write(json.dumps(d) + "\n")

    def _build_dataset(self, questions: List, answers: List) -> List:
        res = []
        for q, a in zip(questions, answers):
            res.append(
                {
                    "instruction": q["question"],
                    "input": q["input"],
                    "output": a["answer"],
                }
            )
        return res

    @abstractmethod
    def _build_question_prompt(self, **kwargs):
        """Build question generation prompt - to be implemented by subclasses"""
        pass

    @abstractmethod
    def _build_answer_prompt(self, **kwargs):
        """Build answer generation prompt - to be implemented by subclasses"""
        pass

    @property
    @abstractmethod
    def question_schema(self):
        """Question schema - to be defined by subclasses"""
        pass

    @property
    @abstractmethod
    def answer_schema(self):
        """Answer schema - to be defined by subclasses"""
        pass
