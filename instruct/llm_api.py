import json
from datetime import datetime
from typing import List

from openai import OpenAI
from pydantic import BaseModel


class Instruction(BaseModel):
    instruction: str
    input: str
    output: str


class Completion(BaseModel):
    completion: list[Instruction]


def make_llm_request(model: str, messages: List, **kwargs):
    try:
        client = OpenAI()

        res = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=Completion,
            **kwargs,
        )
        return json.loads(res.choices[0].message.content)["completion"]
    except Exception as e:
        raise (f"Error processing instructions: {str(e)}")


def make_llm_batch_requst(model: str):
    return
