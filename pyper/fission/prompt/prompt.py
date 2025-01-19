breadth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to create exactly {batch} new tasks inspired by the base tasks given.

Generation Guideline:
1. New task should be in the same domain as the information in the base tasks.
2. Vary sentence structure, vocabularly and tone for maximum diversity
3. The new task has new concepts and is distinct from the original task
4. The new task has equal level of difficulty as the original task
5. The new task has the similar length to the original task.
6. The new task only has factual information and is logically understandable by human

Here are the base tasks:
{base_tasks}
"""

depth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to create exactly {batch} more complex tasks inspired by the base tasks given.


Generation Guideline:
1. New task should be in the same domain as the information in the base tasks.
2. The new task has increased complexity in both information and sentence structure.
3. The new task has similar length to the original task
4. The new task only has factual information and is logically understandable by human

Here are the base task:
{base_tasks}
"""
