import argparse
import time

from fission.generate import FissionGenerator
from gen.src.general_generator import GeneralGenerator
from gen.src.knowledge_generator import KnowledgeGenerator
from pipeline import FissionConfig, GeneralConfig, KnowledgeConfig, Pipeline


def main():
    parser = argparse.ArgumentParser(description="Pyper CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generation command
    gen_parser = subparsers.add_parser("generate", help="Run seed generation")
    gen_parser.add_argument(
        "--mode",
        choices=["general", "knowledge"],
        required=True,
        help="Generation mode",
    )
    gen_parser.add_argument(
        "--num-tasks",
        type=int,
        required=True,
        help="Number of total tasks to generate",
    )
    gen_parser.add_argument(
        "--num-questions",
        type=int,
        required=True,
        help="Number of questions to generate per session",
    )
    gen_parser.add_argument(
        "--max-sessions",
        type=int,
        help="Maximum sessions to generate per subject. Default: 3",
    )
    gen_parser.add_argument("--seed-output", help="Path for seed output file")
    gen_parser.add_argument("--discipline", help="<General>: Discipline to generate")
    gen_parser.add_argument(
        "--max-subjects",
        type=int,
        help="<General>: Maximum subjects to generate. Default: 5",
    )
    gen_parser.add_argument(
        "--max-subtopics",
        type=int,
        help="<General>: Maximum subtopics to generate. Default: 3",
    )
    gen_parser.add_argument(
        "--knowledge-path", help="<Knowledge>: Path to knowledge file to use"
    )

    # Fission command
    fission_parser = subparsers.add_parser("fission", help="Run fission generation")
    fission_parser.add_argument(
        "--num-tasks", type=int, required=True, help="Number of total tasks to generate"
    )
    fission_parser.add_argument(
        "--seed-path", required=True, help="Path to seed data for fission"
    )
    fission_parser.add_argument(
        "--batch",
        type=int,
        help="Number of tasks to generate per iteration. Default: 20",
    )
    fission_parser.add_argument(
        "--num-seed",
        type=int,
        help="Number of tasks to sample from seed pool. Default: 6",
    )
    fission_parser.add_argument(
        "--num-generated",
        type=int,
        help="Number of tasks to sample from generated pool. Default: 2",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(1)
    elif args.command == "generate":
        if args.mode == "general":
            gen_config = GeneralConfig(
                discipline=args.discipline,
                num_tasks=args.num_tasks,
                max_subjects=args.max_subjects,
                max_subtopics=args.max_subtopics,
                max_sessions=args.max_sessions,
                num_questions=args.num_questions,
            )
            generator = GeneralGenerator
        else:
            gen_config = KnowledgeConfig(
                num_tasks=args.num_tasks,
                knowledge_path=args.knowledge_path,
                num_sessions=args.max_sessions,
                num_questions=args.num_questions,
            )
            generator = KnowledgeGenerator

        pipeline = Pipeline(gen=generator)
        pipeline.run(
            seed_output_path=args.seed_output or f"./data/{args.discipline}_seed.jsonl",
            gen_config=gen_config,
        )

    elif args.command == "fission":
        fission_config = FissionConfig(
            num_tasks=args.num_tasks,
            seed_path=args.seed_path,
            batch=args.batch,
            num_seed=args.num_seed,
            num_generated=args.num_generated,
        )
        generator = FissionGenerator

        pipeline = Pipeline(fission=generator)
        pipeline.run(
            result_output_path=f"./data/results_{time.time()}.jsonl",
            fission_config=fission_config,
        )


if __name__ == "__main__":
    main()
