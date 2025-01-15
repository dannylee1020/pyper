from typing import List

import model
from prompt import knowledge_prompt as prompt
from tqdm import tqdm

from pyper.llm_api import make_llm_request

from .base_generator import BaseGenerator


class KnowledgeGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()

    def generate(
        self,
        num_tasks: int,
        knowledge_path: str,
        num_sessions: int,
        num_questions: int,
    ):
        """Generate tasks and answers based on provided knowledge content.

        Args:
            num_tasks (int): Total number of tasks to generate
            knowledge_path (str): Path to the knowledge content file
            num_sessions (int): Number of sessions to generate in the syllabus
            num_questions (int): Number of questions to generate per batch

        Returns:
            tuple: A tuple containing (clean_tasks, answers) where:
                - clean_tasks: List of deduplicated question tasks
                - answers: List of corresponding answers for each task
        """
        print("generating syllabus...")
        syllabus = self._generate_syllabus(
            knowledge_path=knowledge_path,
            max_sessions=num_sessions,
        )
        clean_tasks = []
        with tqdm(total=num_tasks) as pbar:
            while len(clean_tasks) < num_tasks - 1:
                print("generating questions...")
                try:
                    q_res = self._generate_question_task(
                        syllabus=syllabus,
                        batch=num_questions,
                        knowledge=True,
                    )
                except Exception:
                    raise

                clean_t = self._deduplicate_task(q_res)
                clean_tasks.extend(clean_t)
                pbar.update(len(clean_t))

        print("generating answers...")
        answers = self._generate_answers(question_tasks=clean_tasks)

        return clean_tasks, answers

    def _generate_syllabus(self, knowledge_path: str, max_sessions: int = 3) -> List:
        """Generate a syllabus based on provided knowledge content.

        Args:
            knowledge_path (str): Path to the knowledge content file
            max_sessions (int, optional): Maximum number of sessions to generate. Defaults to 3.

        Returns:
            List: Generated syllabus structure based on the knowledge content
        """
        encode_message = [
            {
                "role": "system",
                "content": prompt.generate_syllabus.format(
                    knowledge=open(knowledge_path).read(), max_sessions=max_sessions
                ),
            },
            {
                "role": "user",
                "content": "generate educational syllabus by following the system prompt closely",
            },
        ]

        syllabus = make_llm_request(
            messages=encode_message,
            response_format=model.SyllabusSchema,
        )

        return syllabus

    def _build_question_prompt(self, **kwargs):
        """Knowledge-specific question prompt"""
        return [
            {
                "role": "system",
                "content": prompt.generate_question.format(
                    session=kwargs["session"],
                    concepts=kwargs["concepts"],
                    batch=kwargs["batch"],
                    max_tokens=kwargs["max_tokens"],
                ),
            },
            {
                "role": "user",
                "content": "generate questions by following the system prompt closely",
            },
        ]

    def _build_answer_prompt(self, **kwargs):
        """Knowledge-specific answer prompt"""
        return [
            {
                "role": "system",
                "content": prompt.generate_answer.format(
                    question=kwargs["question"],
                    input=kwargs["input"],
                    max_tokens=kwargs["max_tokens"],
                ),
            },
            {
                "role": "user",
                "content": "generate answer for a given question by following the system prompt closely",
            },
        ]

    @property
    def question_schema(self):
        return model.QuestionSchema

    @property
    def answer_schema(self):
        return model.AnswerSchema
