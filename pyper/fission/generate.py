import json
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Literal

import chromadb
from model import ResponseModel
from prompt import prompt
from pydantic import BaseModel
from tqdm import tqdm

from pyper.llm_api import make_llm_request


class FissionGenerator:
    def __init__(
        self,
        name: str,
        num_tasks: int,
        seed_path: str,
        num_seed: int,
        num_generated: int,
        output_path: str = None,
    ):
        """Initialize FissionGenerator with configuration parameters.

        Args:
            name (str): Name to use for result dataset
            num_tasks (int): Total number of items to generate
            seed_path (str): Path to seed data
            num_seed (int): Number of seed tasks to sample in each iteration
            num_generated (int): Number of generated tasks to sample in each iteration
            output_path (str, optional): Custom output path for results. Defaults to None.
        """
        self.num_tasks = num_tasks
        self.seed_path = seed_path
        self.num_seed = num_seed
        self.num_generated = num_generated
        self.output_path = output_path or f"../data/{name}_results.jsonl"

        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection("instruction")
        self.seed_pool = []
        self.gen_pool = []
        self.clean_tasks = []

    def _generate_breadth(self, batch: int, instructions: List) -> Dict[str, Any]:
        encode_message = [
            {
                "role": "system",
                "content": prompt.breadth_prompt.format(
                    batch=batch,
                    base_tasks=instructions,
                ),
            },
            {
                "role": "user",
                "content": f"generate exactly {batch} task instructions by following the system promptly exactly.",
            },
        ]
        return make_llm_request(
            messages=encode_message,
            response_format=ResponseModel,
        )

    def _generate_depth(self, batch: int, instructions: List) -> Dict[str, Any]:
        encode_message = [
            {
                "role": "system",
                "content": prompt.depth_prompt.format(
                    batch=batch,
                    base_tasks=instructions,
                ),
            },
            {
                "role": "user",
                "content": f"generate exactly {batch} task instructions by following the system prompt exactly",
            },
        ]

        return make_llm_request(
            messages=encode_message,
            response_format=ResponseModel,
        )

    def _initialize_chroma(self):
        """Initializes chromadb and add seed data for embedding based similarity"""
        self.collection = self.chroma.create_collection("generation_pool")
        seed_texts = [item["instruction"] for item in self.seed_pool]

        print("adding seed data to chroma...")
        self.collection.add(
            documents=seed_texts, ids=[f"seed_{i}" for i in range(len(seed_texts))]
        )

    def _deduplicate_instruction(self, instructions: List, pbar: tqdm) -> int:
        """Remove similar tasks based on instruction similarity."""
        print("filtering similar items...")
        cnt = 0
        for new_inst in instructions:
            results = self.collection.query(
                query_texts=[new_inst["instruction"]], n_results=1
            )

            if not results["distances"][0] or results["distances"][0][0] > 0.7:
                self.collection.add(
                    documents=[new_inst["instruction"]],
                    ids=[f"gen_{len(self.clean_tasks)}"],
                )

                self.clean_tasks.append(new_inst)
                self.gen_pool.append(new_inst)
                pbar.update(1)
                cnt += 1

            if len(self.clean_tasks) >= self.num_tasks:
                return cnt

    def _create_seed_pool(self, seed_path: str) -> List:
        with open(seed_path, "r") as f:
            for line in f:
                if line.strip():
                    self.seed_pool.append(json.loads(line))

        return self.seed_pool

    def _parse_samples(self, samples: List):
        template = """# Task {num}: \n instruction: {instruction} \n input: {input} \n output: {output} \n\n"""
        parsed = ""
        for i, sample in enumerate(samples):
            parsed += template.format(
                num=i,
                instruction=sample["instruction"],
                input=sample["input"],
                output=sample["output"],
            )

        return parsed

    def generate(self):
        """Main generation process.

        Executes the full instruction generation pipeline:
        1. Loads seed data
        2. Initializes ChromaDB
        3. Generates new instructions using both breadth and depth approaches
        4. Deduplicates and filters similar instructions
        5. Saves results to output file
        """
        self._create_seed_pool(self.seed_path)
        self._initialize_chroma()

        with tqdm(total=self.num_tasks) as pbar:
            print("starting generation...")
            while len(self.clean_tasks) < self.num_tasks:
                batch = self.num_seed + self.num_generated
                sample_seed = random.sample(self.seed_pool, self.num_seed)
                if self.gen_pool:
                    gen_pool = random.sample(self.gen_pool, self.num_generated)
                    combined_sample = sample_seed + gen_pool
                else:
                    combined_sample = sample_seed
                parsed_sample = self._parse_samples(samples=combined_sample)

                print("requesting LLM output...")
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_breadth = executor.submit(
                        self._generate_breadth,
                        batch=batch,
                        instructions=parsed_sample,
                    )
                    future_depth = executor.submit(
                        self._generate_depth,
                        batch=batch,
                        instructions=parsed_sample,
                    )

                    b_inst = future_breadth.result()
                    d_inst = future_depth.result()

                generated_inst = []
                generated_inst.extend(
                    [
                        {
                            "instruction": i["instruction"],
                            "input": i["input"],
                            "output": i["output"],
                        }
                        for i in b_inst["tasks"]
                    ]
                )
                generated_inst.extend(
                    [
                        {
                            "instruction": i["instruction"],
                            "input": i["input"],
                            "output": i["output"],
                        }
                        for i in d_inst["tasks"]
                    ]
                )
                print(f"# generated questions: {len(generated_inst)}")
                cnt = self._deduplicate_instruction(generated_inst, pbar)
                print(f"# questions after filtering: {cnt}")

        self.save_results()

    def save_results(self):
        """Save generated tasks to output file in JSONL format."""
        with open(self.output_path, "w") as f:
            for i in self.clean_tasks:
                f.write(json.dumps(i) + "\n")
