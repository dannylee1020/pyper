import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Union

from fission.generate import FissionGenerator
from gen.src.general_generator import GeneralGenerator
from gen.src.knowledge_generator import KnowledgeGenerator


@dataclass
class GeneralConfig:
    discipline: str
    num_tasks: int
    num_questions: int
    max_subjects: int = 5
    max_subtopics: int = 3
    max_sessions: int = 5


@dataclass
class KnowledgeConfig:
    num_tasks: int
    knowledge_path: str
    num_sessions: int
    num_questions: int


@dataclass
class FissionConfig:
    num_tasks: int
    seed_path: str
    batch: int = 20
    num_seed: int = 6
    num_generated: int = 2


class Pipeline:
    """A pipeline for generating and processing educational tasks.

    This pipeline combines two main components:
    1. A generator (either GeneralGenerator or KnowledgeGenerator) that creates initial seed tasks
    2. A FissionGenerator that takes the seed tasks and generates variations

    The process involves:
    1. Generating seed tasks using the configured generator
    2. Writing these seed tasks to a file
    3. Using FissionGenerator to create variations based on the seed tasks
    """

    def __init__(
        self,
        gen: Union[GeneralGenerator, KnowledgeGenerator] = None,
        fission: FissionGenerator = None,
    ):
        """Initialize the pipeline with generator components.

        Args:
            gen: Either a GeneralGenerator (for discipline-based generation) or
                KnowledgeGenerator (for knowledge-based generation)
            fission: FissionGenerator instance for creating task variations
        """
        self.gen = gen
        self.fission = fission

    def _save_results(self, data: List, output_path: str):
        """Common method to save results"""
        with open(output_path, "w") as f:
            for l in data:
                f.write(json.dumps(l) + "\n")

    def run(
        self,
        seed_output_path: str = None,
        result_output_path: str = None,
        gen_config: Union[GeneralConfig, KnowledgeConfig] = None,
        fission_config: FissionConfig = None,
    ) -> None:
        """Run the complete pipeline to generate and process tasks.

        Args:
            gen_config: Configuration for the generator (either GeneralConfig or KnowledgeConfig)
            fission_config: Configuration for the FissionGenerator

        Raises:
            ValueError: If the generator type doesn't match the config type
        """
        # Generate seed data based on generator type
        if self.gen:
            print("Starting seed generation...")
            generator = self.gen()
            if isinstance(self.gen, (type(GeneralGenerator))):
                if not isinstance(gen_config, GeneralConfig):
                    raise ValueError("GeneralGenerator requires GeneralConfig")

                seed = generator.generate(**asdict(gen_config))
            elif isinstance(self.gen, (type(KnowledgeGenerator))):
                if not isinstance(gen_config, KnowledgeConfig):
                    raise ValueError("KnowledgeGenerator requires KnowledgeConfig")

                seed = generator.generate(**asdict(gen_config))
            else:
                raise ValueError(f"Unsupported generator type: {type(self.gen)}")

            # write seed to the file
            self._save_results(
                data=seed,
                output_path=seed_output_path,
            )
            print("Finished generating seed...")

        if self.fission:
            # Run fission generation
            print("Starting fission...")
            fission = self.fission()
            final = fission.generate(**asdict(fission_config))
            self._save_results(
                data=final,
                output_path=result_output_path,
            )
            print("Finished generation!")
