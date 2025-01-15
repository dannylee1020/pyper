import fire
from generate import FissionGenerator


def generate(
    name: str,
    num_tasks: int,
    seed_path: str,
    num_seed: int = 5,
    num_generated: int = 2,
    output_path: str = None,
):
    """Main function for generating instruction tasks based on seed data.

    Args:
        name (str): Name to use for result dataset
        num_instructions (int): Total number of items to generate
        seed_path (str): Path to seed data file
        num_seed (int, optional): Number of seed items to use in each generation. Defaults to 5.
        num_generated (int, optional): Number of items to generate in each iteration. Defaults to 2.
        output_path (str, optional): Custom output path for results. Defaults to None.
    """
    generator = FissionGenerator(
        name=name,
        num_tasks=num_tasks,
        seed_path=seed_path,
        num_seed=num_seed,
        num_generated=num_generated,
        output_path=output_path,
    )
    generator.generate()


if __name__ == "__main__":
    fire.Fire(generate)
