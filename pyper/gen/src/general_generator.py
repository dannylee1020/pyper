import json
from typing import List

import fire
import model
from prompt import general_prompt as prompt
from tqdm import tqdm

from pyper.llm_api import make_llm_request

from .base_generator import BaseGenerator


class GeneralGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()

    def generate(
        self,
        discipline: str,
        num_tasks: int,
        max_subjects: int,
        max_subtopics: int,
        max_sessions: int,
        num_questions: int,
    ):
        """Generate tasks and answers for a given discipline.

        Args:
            discipline (str): The academic discipline to generate content for
            num_tasks (int): Total number of tasks to generate
            max_subjects (int): Maximum number of subjects to generate
            max_subtopics (int): Maximum number of subtopics per subject
            max_sessions (int): Maximum number of sessions per syllabus
            num_questions (int): Number of questions to generate per batch

        Returns:
            tuple: A tuple containing (clean_tasks, answers) where:
                - clean_tasks: List of deduplicated question tasks
                - answers: List of corresponding answers for each task
        """
        print("generating subjects...")
        subjects = self._generate_subject(
            discipline=discipline,
            max_subjects=max_subjects,
            max_subtopics=max_subtopics,
        )
        print("generating syllabus...")
        syllabus = self._generate_syllabus(
            subjects=subjects,
            max_sessions=max_sessions,
        )

        clean_tasks = []
        with tqdm(total=num_tasks) as pbar:
            while len(clean_tasks) < num_tasks - 1:
                print("generating questions...")
                try:
                    q_res = self._generate_question_task(
                        syllabus=syllabus,
                        batch=num_questions,
                        knowledge=False,
                    )
                except Exception:
                    raise

                clean_t = self._deduplicate_task(q_res)
                clean_tasks.extend(clean_t)
                pbar.update(len(clean_t))

        print("generating answers...")
        answers = self._generate_answers(question_tasks=clean_tasks)

        return clean_tasks, answers

    def _generate_subject(
        self,
        discipline: str,
        max_subjects: int,
        max_subtopics: int,
    ):
        """Generate subjects for the discipline"""
        encode_message = [
            {
                "role": "system",
                "content": prompt.generate_subject.format(
                    discipline=discipline,
                    max_subjects=max_subjects,
                    max_subtopics=max_subtopics,
                ),
            },
            {
                "role": "user",
                "content": f"generate comprehensive list of subjects in {discipline} following the system prompt closely",
            },
        ]

        res = make_llm_request(
            messages=encode_message,
            response_format=model.SubjectSchema,
        )

        return res

    def _generate_syllabus(
        self,
        subjects: List,
        max_sessions: int,
    ) -> List:
        """Generate syllabus for each subject"""
        syllabus = []
        for s in subjects["subjects"]:
            subject = s["subject"]
            level = s["level"]
            subtopics = s["subtopics"]

            encode_message = [
                {
                    "role": "system",
                    "content": prompt.generate_syllabus.format(
                        subject=subject,
                        level=level,
                        subtopics=subtopics,
                        max_sessions=max_sessions,
                    ),
                },
                {
                    "role": "user",
                    "content": "generate educational syllabus by following the system prompt closely",
                },
            ]

            syllabi = make_llm_request(
                messages=encode_message,
                response_format=model.SyllabusSchema,
            )
            syllabus.append(syllabi)

        return syllabus

    def _build_question_prompt(self, **kwargs):
        """General question prompt"""
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
                "content": "generate homework questions based on the syllabus by following the system prompt closely",
            },
        ]

    def _build_answer_prompt(self, **kwargs):
        """General answer prompt"""
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
