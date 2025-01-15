from typing import List

from pydantic import BaseModel


# subject model
class Subject(BaseModel):
    subject: str
    level: int
    subtopics: List[str]


class SubjectSchema(BaseModel):
    subjects: List[Subject]


# syllabus model
class Session(BaseModel):
    session_name: str
    description: str
    key_concepts: List[str]


class SyllabusSchema(BaseModel):
    subject: str
    subtopics: List[str]
    syllabus: List[Session]


# questions model
class Question(BaseModel):
    question: str
    input: str


# need this to make model generate multiple questions
class QuestionSchema(BaseModel):
    questions: List[Question]


# answer model
class AnswerSchema(BaseModel):
    answer: str
