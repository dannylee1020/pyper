import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Literal

import chromadb
from pydantic import BaseModel
from tqdm import tqdm

from pyper.llm_api import make_llm_request

from .model import ResponseModel
from .prompt import prompt


class FissionGenerator:
    def __init__(self):
        """Initialize FissionGenerator with chromadb client."""
        self.chroma = chromadb.Client()

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

    def _initialize_chroma(self, seed_pool: List[Dict]):
        """Initializes chromadb and add seed data for embedding based similarity

        Args:
            seed_pool: List of seed tasks to initialize the collection with

        Returns:
            chromadb.Collection: Initialized collection with seed data
        """
        collection = self.chroma.create_collection("generation_pool")
        seed_texts = [item["instruction"] for item in seed_pool]

        print("adding seed data to chroma...")
        collection.add(
            documents=seed_texts, ids=[f"seed_{i}" for i in range(len(seed_texts))]
        )

        return collection

    def _deduplicate_instruction(
        self,
        instructions: List,
        collection: chromadb.Collection,
        pbar: tqdm,
        res_length: int,
        num_tasks: int,
    ) -> tuple[List, int]:
        """Remove similar tasks based on instruction similarity.

        Args:
            instructions: List of new instructions to deduplicate
            collection: ChromaDB collection for similarity checking
            pbar: Progress bar to update
            res_length: Current length of results
            num_tasks: Total number of tasks to generate

        Returns:
            tuple containing:
            - List of clean tasks
            - Count of new tasks added
        """
        print("filtering similar items...")
        cnt = 0
        clean_tasks = []
        for new_inst in instructions:
            results = collection.query(
                query_texts=[new_inst["instruction"]], n_results=1
            )

            if not results["distances"][0] or results["distances"][0][0] > 0.7:
                collection.add(
                    documents=[new_inst["instruction"]],
                    ids=[f"gen_{time.time()}"],
                )

                clean_tasks.append(new_inst)
                pbar.update(1)
                cnt += 1

            if res_length > num_tasks:
                return clean_tasks, cnt

        return clean_tasks, cnt

    def _create_seed_pool(self, seed_path: str) -> List:
        """Create initial seed pool from file

        Args:
            seed_path: Path to seed data file

        Returns:
            List of seed tasks
        """
        seed_pool = []
        with open(seed_path, "r") as f:
            for line in f:
                if line.strip():
                    seed_pool.append(json.loads(line))

        return seed_pool

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

    def generate(
        self,
        num_tasks: int,
        seed_path: str,
        batch: int,
        num_seed: int,
        num_generated: int,
    ) -> List:
        """Main generation process.

        Args:
            num_tasks (int): Total number of items to generate
            seed_path (str): Path to seed data file
            batch (int): How many tasks to generate for each iteration
            num_seed (int): Number of seed tasks to sample in each iteration
            num_generated (int): Number of generated tasks to sample in each iteration

        Returns:
            List: Generated and filtered tasks
        """
        # Initialize data
        seed_pool = self._create_seed_pool(seed_path)
        collection = self._initialize_chroma(seed_pool)
        clean_tasks = []
        gen_pool = []
        num_q = int(batch // 2)

        with tqdm(total=num_tasks) as pbar:
            print("starting generation...")
            while len(clean_tasks) < num_tasks:
                sample_seed = random.sample(seed_pool, num_seed)
                if gen_pool:
                    gen_samples = random.sample(gen_pool, num_generated)
                    combined_sample = sample_seed + gen_samples
                else:
                    combined_sample = sample_seed
                parsed_sample = self._parse_samples(samples=combined_sample)

                print("requesting LLM output...")
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_breadth = executor.submit(
                        self._generate_breadth,
                        batch=num_q,
                        instructions=parsed_sample,
                    )
                    future_depth = executor.submit(
                        self._generate_depth,
                        batch=batch - num_q,
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
                filtered, cnt = self._deduplicate_instruction(
                    instructions=generated_inst,
                    collection=collection,
                    pbar=pbar,
                    res_length=len(clean_tasks),
                    num_tasks=num_tasks,
                )
                print(f"# questions after filtering: {cnt}")
                # add to result list
                clean_tasks.extend(filtered)
                # add to pool for sampling
                gen_pool.extend(filtered)

        return clean_tasks
