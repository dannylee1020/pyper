generate_subject = """
You are an expert professor in {discipline}. Create a list of subjects a student should learn under this discipline.
For each subject, provide the level (ranging between 100 - 900) and include key subtopics.

Generation guideline:
1. Limit the number of subjects generated to a maximum of {max_subjects}.
2. The list of subjects covers the majority of the knowledge in the discipline.
3. Limit the number of subtopics to a maximum of {max_subtopics} for each `subject`.

"""

generate_syllabus = """
You are an expert professor tasked with creating educational syllabus. Create a detailed syllabus for the subject "{subject}" at the {level} level.

Generation Guideline:
1. The syllabus should be broken down into multiple class sessions, each covering different key concepts.
2. The subtopics for this subject include: {subtopics}.
3. Limit the number of sessions to a maximum of {max_sessions}.
"""

generate_question = """
Based on the class session(s) {session} and key concepts {concepts}, generate exactly {batch} homework questions.

Generation Guideline:
1. Generate an appropriate input to the question. The input field should contain a specific example provided for the question. It should involve realistic data and should not contain simple placeholders. The input should provide substantial content to make the question challenging.
2. Not all questions require input. For example, when a question asks about some general information, "what is the highest peak in the world", it is not necssary to provide a specific context. In this case, put "" in the input field.
3. Vary the style of the questions by generating each type where applicable: Remeber, Understand, Apply, Analyze and Evaluate.
4. Questions have varying difficulty from easy, medium and hard
5. Questions are concise with maximum of {max_tokens} tokens.
"""


generate_answer = """
Answer the question. Keep the answer short and concise. The topic, level, and subtopic of this question are as follows.

## Question: {question}
## Input: {input}

Generation Guideline:
1. Respond "DO NOT KNOW" if not sure about the answer.
2. Answers are concise with the maximum length of {max_tokens} tokens.
"""
