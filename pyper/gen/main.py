from typing import List

import fire
from src.general_generator import GeneralGenerator
from src.knowledge_generator import KnowledgeGenerator


def generate(
    discipline: str,
    num_tasks: int,
    max_subjects: int = 5,
    max_subtopics: int = 3,
    max_sessions: int = 3,
    num_questions: int = 5,
):
    """
    Main function for generating seed data.
    Args:
        discipline: discipline to generat data for
        num_instructions:
        max_subjects: maximum number of subjects to generate
        max_subtopics: maximum number of subtopics to have per subject
        max_sessions: maximum number of sessions to have per syllabi
        num_instructions: number of total instructions to generate
        num_questions: number of questions to generate for each session in a given syllabi. Total question generated is num_sessions * num_questions
    """
    generator = GeneralGenerator()
    questions, answers = generator.generate(
        discipline=discipline,
        num_tasks=num_tasks,
        max_subjects=max_subjects,
        max_subtopics=max_subtopics,
        max_sessions=max_sessions,
        num_questions=num_questions,
    )

    generator.save_results(
        questions=questions,
        answers=answers,
        output_path=f"../data/results_{discipline}.jsonl",
    )


def generate_with_knowledge(
    name: str,
    num_tasks: int,
    knowledge_path: str,
    num_sessions: int = 2,
    num_questions: int = 3,
):
    """
    Main function for generating seed data with knowledge.
    Args:
        name: name of the knowledge
        num_tasks: number of tasks to generate
        knowledge_path: path to the knowledge source
        num_sessions: number of sessions to generate per syllabi
        num_questions: number of questions to generate per session
    """
    generator = KnowledgeGenerator()
    questions, answers = generator.generate(
        num_tasks=num_tasks,
        knowledge_path=knowledge_path,
        num_sessions=num_sessions,
        num_questions=num_questions,
    )

    generator.save_results(
        questions=questions,
        answers=answers,
        output_path=f"../data/results_{name}.jsonl",
    )


if __name__ == "__main__":
    fire.Fire(
        {
            "generate": generate,
            "generate_with_knowledge": generate_with_knowledge,
        }
    )
