import json
from typing import List

import fire
import model
import prompt
from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema
from tqdm import tqdm

from pyper.llm_api import make_llm_batch_request, make_llm_request


def _generate_syllabus(knowledge_path: str):
    encode_message = [
        {
            "role": "user",
            "content": prompt.generate_syllabus_knowledge.format(
                knowledge=open(knowledge_path).read(),
                limit=3,
            ),
        }
    ]

    res = make_llm_request(
        messages=encode_message,
        response_format=model.SyllabusSchema,
    )
    return res


def _generate_questions(
    syllabus: List,
    batch: int,
    max_tokens: int,
):
    subject = syllabus["subject"]
    subtopics = syllabus["subtopics"]
    syl = syllabus["syllabus"]

    tasks = []
    for i, s in enumerate(syl):
        session = s["session_name"]
        concepts = s["key_concepts"]
        encode_message = [
            {
                "role": "system",
                "content": prompt.generate_questions_knowledge.format(
                    session=session,
                    concepts=concepts,
                    batch=batch,
                    max_tokens=max_tokens,
                    subject=subject,
                    subtopics=subtopics,
                ),
            },
            {
                "role": "user",
                "content": "generate questions by following the system prompt closely",
            },
        ]

        tasks.append(
            {
                "custom_id": f"batch_req_{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": encode_message,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "response_schema",
                            "description": "schema for response format",
                            "strict": True,
                            "schema": to_strict_json_schema(model.QuestionSchema),
                        },
                    },
                    "max_tokens": 4096,
                },
            }
        )

    batch_info = make_llm_batch_request(
        tasks=tasks,
        response_format=model.QuestionSchema,
    )
    return batch_info


def generate_questions(
    num_request: int,
    knowledge_path: str,
    num_questions: int,
):
    """generates questions with batch processing."""

    print("generating syllabus...")
    syllabus = _generate_syllabus(knowledge_path=knowledge_path)

    batch_infos = []
    total = 0
    with tqdm(total=num_request) as pbar:
        while total < num_request:
            print("requesting batch processing...")
            batch_info = _generate_questions(
                syllabus=syllabus,
                batch=num_questions,
                max_tokens=100,
            )
            total += num_questions
            batch_infos.append(batch_info)
            pbar.update(total)

    return batch_infos


def retrieve_batch_results(batch_ids: List) -> List:
    client = OpenAI()

    results = []
    for id in batch_ids:
        status = client.batches.retrieve(id)
        if status.output_file_id is None:
            print(f"batch {id} can't be retrieved. Status: {status.status}")
            return

        res = client.files.content(status.output_file_id).content
        for line in res.decode("utf-8").splitlines():
            json_obj = json.loads(line)
            results.append(json_obj)

    return results


def _generate_answers(questions: List):
    tasks = []
    for i, q in enumerate(questions):
        c = q["response"]["body"]["choices"][0]["message"]["content"]
        subject = c["subject"]
        subtopics = c["subtopics"]
        question = c["question"]
        input = c["input"]

        encode_message = [
            {
                "role": "user",
                "content": prompt.generate_answers_knowledge.format(
                    subject=subject,
                    subtopics=subtopics,
                    question=question,
                    input=input,
                ),
            }
        ]

        tasks.append(
            {
                "custom_id": f"batch_req_{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": encode_message,
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "response_schema",
                            "description": "schema for response format",
                            "strict": True,
                            "schema": to_strict_json_schema(model.AnswerSchema),
                        },
                    },
                    "max_tokens": 4096,
                },
            }
        )

    batch_info = make_llm_batch_request(
        tasks=tasks,
        response_format=model.AnswerSchema,
    )

    return batch_info


def generate_answers(questions: List):
    batch_info = _generate_answers(questions)
    return batch_info


if __name__ == "__main__":
    q_batch = generate_questions(
        num_request=1,
        knowledge_path="../source/knowledge.txt",
        num_questions=2,
    )

    # questions = retrieve_batch_results(
    #     batch_ids=["batch_67830aaa80848190a2f5b1703e28f5da"]
    # )

    print(questions)
