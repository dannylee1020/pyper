import json
import os
import random
import re
import string
import time
from functools import partial
from multiprocessing import Pool
from typing import Dict, List

import fire
import numpy as np
from rouge_score import rouge_scorer
from tqdm import tqdm

from llm_api import make_llm_request
from source.prompt import context_prompt, instruction_prompt


def find_word_in_string(w, s):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(s)


def post_process_response(response: List[Dict]):
    if not response:
        return []

    instructions = []
    for item in response:
        inst = item["instruction"].strip()
        input_text = item["input"].strip()
        output = item["output"].strip()

        # filter if both input and output are missing
        if len(input_text) == 0 and len(output) == 0:
            continue

        # filter out too short or too long instructions
        if len(inst.split()) <= 3 or len(inst.split()) > 150:
            continue

        # filter out too long output
        if len(output.split()) > 150:
            continue

        # filter based on keywords that are not suitable for language models
        blacklist = [
            "image",
            "images",
            "graph",
            "graphs",
            "picture",
            "pictures",
            "file",
            "files",
            "map",
            "maps",
            "draw",
            "plot",
            "go to",
            "video",
            "audio",
            "music",
            "flowchart",
            "diagram",
        ]

        if any(find_word_in_string(word, inst) for word in blacklist):
            continue

        # Filter out programming instructions
        if inst.startswith("Write a program"):
            continue

        # filter those starting with punctuation
        if inst[0] in string.punctuation:
            continue

        # filter those starting with non-english character
        if not inst[0].isascii():
            continue

        input_text = "" if input_text.lower() == "<noinput>" else input_text

        instructions.append(
            {"instruction": inst, "input": input_text, "output": output}
        )

    return instructions


def encode_message(
    prompts: List[Dict],
    batch: int,
    knowledge: bool = False,
    knowledge_dir: str = None,
):
    """
    encode multiple instructions into single prompt for chat completion
    """
    if knowledge:
        knowledge = open(knowledge_dir).read()
        system_message = {
            "role": "system",
            "content": context_prompt.format(batch, knowledge),
        }
    else:
        system_message = {"role": "system", "content": instruction_prompt.format(batch)}

    example_content = ""
    for idx, task_dict in enumerate(prompts):
        instruction = task_dict["instruction"].strip().rstrip(":")
        input = "<noinput>" if task_dict["input"].lower() == "" else task_dict["input"]
        output = task_dict["output"]

        example_content += f"Example {idx + 1}: \n"
        example_content += f"Instruction: {instruction} \n"
        example_content += f"Input: {input} \n"
        example_content += f"Output: {output}\n\n"

    example_content += "Generate the instructions following the same format."

    user_message = {"role": "user", "content": example_content}

    return [system_message, user_message]


def generate(
    num_instructions: int = 30,
    model: str = "gpt-4o",
    output_dir: str = "./data",
    knowledge_dir: str = None,
    batch: int = 10,
    num_sample_seed: int = 6,
    num_sample_machine: int = 2,
    temperature: float = None,
    top_p: float = None,
    frequency_penalty: float = None,
    max_tokens: int = 2048,
):
    """
    Generate instruction-following data using a language model.

    This function generates instruction-following data by combining seed tasks with machine-generated
    instructions. It uses a language model to generate new instructions and applies various filtering
    techniques to ensure quality and uniqueness.

    Args:
        num_instructions (int, optional): Total number of instructions to generate. Defaults to 30.
        model (str, optional): Name of the language model to use. Defaults to "gpt-4o".
        output_dir (str, optional): Directory to save generated instructions. Defaults to "./data".
        knowledge_dir (str, optional): Path to knowledge file for context-based generation. Defaults to None.
        batch (int, optional): Number of instructions to generate per request. Defaults to 10.
        num_sample_seed (int, optional): Number of seed tasks to sample for each generation. Defaults to 6.
        num_sample_machine (int, optional): Number of machine-generated tasks to sample. Defaults to 2.
        temperature (float, optional): Sampling temperature for the language model. Defaults to None (1.1).
        top_p (float, optional): Top-p sampling parameter. Defaults to None (0.5).
        frequency_penalty (float, optional): Frequency penalty for generation. Defaults to None (1.0).
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 2048.

    """
    request_idx = 0
    seed_tasks = [json.loads(l) for l in open("./data/seed_tasks.jsonl", "r")]
    seed_tasks = [
        {
            "instruction": t["instruction"],
            "input": t["instances"][0]["input"],
            "output": t["instances"][0]["output"],
        }
        for t in seed_tasks
    ]

    print(f"Loaded {len(seed_tasks)} seed instructions")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # load machine generated data for sampling
    lm_generated_data = []
    poolname = "lm_knowledge_pool.json" if knowledge_dir else "lm_instruction_pool.json"
    lm_gen_path = os.path.join(output_dir, poolname)
    if os.path.exists(lm_gen_path):
        with open(lm_gen_path, "r") as fin:
            lm_generated_data = json.load(fin)
            print(f"Loaded {(len(lm_generated_data))} machine-generated instructions")

    # init scorere for similarity check later
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    # tokenize all instruction for similarity check
    all_instructions = [d["instruction"] for d in seed_tasks] + [
        d["instruction"] for d in lm_generated_data
    ]
    all_instruction_tokens = [
        scorer._tokenizer.tokenize(inst) for inst in all_instructions
    ]

    with tqdm(total=num_instructions, desc="Generating instructions") as pbar:
        while len(lm_generated_data) < num_instructions:
            request_idx += 1
            sample_seed_tasks = random.sample(seed_tasks, num_sample_seed)

            if len(lm_generated_data) > 0:
                sample_lm_tasks = random.sample(lm_generated_data, num_sample_machine)
            else:
                sample_lm_tasks = []

            combined_sample = sample_seed_tasks + sample_lm_tasks

            # if generation with knowledge, encode accordingly.
            if knowledge_dir:
                encoded_message = encode_message(
                    prompts=combined_sample,
                    batch=batch,
                    knowledge=True,
                    knowledge_dir=knowledge_dir,
                )
            else:
                encoded_message = encode_message(
                    prompts=combined_sample,
                    batch=batch,
                )

            # generate instructions
            req_start = time.time()
            results = make_llm_request(
                model=model,
                messages=encoded_message,
                temperature=temperature or 1.1,
                top_p=top_p or 0.5,
                frequency_penalty=frequency_penalty or 1.0,
            )
            req_duration = time.time() - req_start

            # process instructions
            process_start = time.time()
            processed_instructions = post_process_response(results)

            # compute similarity for further filtering
            keep = 0
            for inst in processed_instructions:
                inst_tokens = scorer._tokenizer.tokenize(inst["instruction"])
                with Pool(4) as p:
                    rouge_scores = p.map(
                        partial(rouge_scorer._score_lcs, inst_tokens),
                        all_instruction_tokens,
                    )
                rouge_scores = [score.fmeasure for score in rouge_scores]

                # filter too similar instruction
                if max(rouge_scores) > 0.7:
                    continue

                lm_generated_data.append(inst)
                all_instructions.append(inst["instruction"])
                all_instruction_tokens.append(inst_tokens)
                keep += 1

            process_duration = time.time() - process_start
            pbar.set_postfix(
                {
                    "request": request_idx,
                    "req_time": f"{req_duration:.1f}s",
                    "proc_time": f"{process_duration:.1f}s",
                    "kept": keep,
                }
            )
            pbar.update(keep)

            print(f"Generated {len(processed_instructions)}, kept {keep} instructions")

            # write filtered instruction back to the pool
            with open(lm_gen_path, "w") as fout:
                json.dump(lm_generated_data, fout, indent=4, default=str)


if __name__ == "__main__":
    fire.Fire(generate)
