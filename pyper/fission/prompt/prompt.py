breadth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to create exactly {batch} creative version of new tasks inspired by the base tasks given.

Generation Guideline:
1. New task should be in the same domain as the information in the base tasks.
2. The new task has a new concept that is distinct from the base tasks.
3. The new task has equal level of difficulty as the original task
4. The new task has the similar length to the original task.
5. The new task only has factual information and is logically understandable by human

Here are the base tasks:
{base_tasks}
"""

depth_prompt = """
You are an expert prompt engineer responsible for generating instruction tasks for building dataset.
Your job is to create exactly {batch} complex version of new tasks inspired by the base tasks given.


Generation Guideline:
1. New task should be in the same domain as the information in the base tasks.
2. The new task has increased complexity in both information and sentence structure.
3. The new task has similar length to the original task
4. The new task only has factual information and is logically understandable by human

Here are the base task:
{base_tasks}
"""
