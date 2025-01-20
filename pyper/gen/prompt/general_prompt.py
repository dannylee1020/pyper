generate_subject = """
You are an expert professor in {discipline}. Create a list of subjects a student should learn under this discipline.
For each subject, provide the level (ranging between 100 - 900) and include key subtopics.

Generation guideline:
1. Limit the number of subjects generated to a maximum of {max_subjects}.
2. The list of subjects covers the majority of the knowledge in the discipline.
3. Limit the number of subtopics to a maximum of {max_subtopics} for each `subject`.

"""

generate_syllabus = """
You are an expert tasked with creating syllabus. Create a detailed syllabus for the subject: {subject} at the level: {level}

Generation Guideline:
1. The syllabus should be broken down into multiple class sessions, each covering different key concepts.
2. The subtopics for this subject include: {subtopics}.
3. Limit the number of sessions to a maximum of {max_sessions}.
"""

generate_question = """
Based on the class session(s) {session} and key concepts {concepts}, generate exactly {batch} homework tasks.

Generation Guideline:
1. Generate an appropriate input to the question. The input field should contain a specific example provided for the question. If input is not necessary, return ""

<example>
Instruction: What is the relation between the given pairs?
Input: Night : Day :: Right : Left
Output: The relation between the given pairs is that they are opposites.

Instruction: Generate a haiku using the following word
Input: summer
Output: The chill, worming in\nShock, pleasure, bursting within\nSummer tongue awakes
</example>

2. Generate balanced number of tasks with and without the input field.
3. Vary the style of the questions by generating each type where applicable: Remeber, Understand, Apply, Analyze and Evaluate.
4. Questions have varying difficulty from easy, medium and hard
5. Questions are concise with maximum of {max_tokens} tokens.
"""


generate_answer = """
Answer the question correctly and logically. Make your answer short and concise.

## Question: {question}
## Input: {input}

Generation Guideline:
1. Respond "DO NOT KNOW" if not sure about the answer.
2. Answers are concise with the maximum length of {max_tokens} tokens.

Only generate characters that are not JSON control characters (\u0000-\u001F).
"""
