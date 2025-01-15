import json
import os
from datetime import datetime
from typing import List

from openai import OpenAI
from openai.lib._pydantic import to_strict_json_schema


def make_llm_request(
    messages,
    response_format,
    **kwargs,
):
    client = OpenAI()
    try:
        res = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            response_format=response_format,
            max_tokens=15000,
            **kwargs,
        )

        return json.loads(res.choices[0].message.content)
    except Exception as e:
        raise Exception(f"error generating response from model: {str(e)}")


def make_llm_batch_request(
    tasks: List,
    response_format,
):
    try:
        client = OpenAI()

        data_dir = "./batch"
        os.makedirs(data_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_dir}/batch_tasks_{timestamp}.jsonl"
        with open(filename, "w") as f:
            for t in tasks:
                f.write(json.dumps(t) + "\n")

        batch_file = client.files.create(file=open(filename, "rb"), purpose="batch")

        batch_job = client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        return batch_job
    except Exception as e:
        raise Exception(f"Error processing batch request: {str(e)}")
