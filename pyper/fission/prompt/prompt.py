breadth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to evolve given tasks into new, creative version. Create exactly {batch} new tasks for increased creativity and diversity.

Generation Guideline:
1. Vary sentence structure, vocabularly and tone for maximum diversity
2. The new task has new concepts and is distinct from the original task
3. The new task has equal level of difficulty as the original task
4. The new task has the similar length to the original task.
5. The new task only has factual information and is logically understandable by human

Here are the base tasks:
{base_tasks}
"""

depth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to evolve given tasks into more complex version. Create exactly {batch} new tasks for increased difficulty and complexity.

Generation Guideline:
1. The new task is in the same domain as the original task
2. The new task has more details and complex concepts than the original task
3. The new task has similar length to the original task
4. The new task only has factual information and is logically understandable by human

Here are the base task:
{base_tasks}
"""
