generate_syllabus = """
You are an expert in creating educational syallbus. Create a detailed syllabus for the provided knowledge:

{knowledge}

Generation Guideline:
1. The syllabus should be broken down into multiple class sessions, each covering different key concepts.
2. The syllabus covers the information provided in the provided knowledge
3. Generate as many syllabi as needed to fully cover the provided knowledge
3. Limit the number of sessions to a maximum of {max_sessions}.
"""

generate_question = """
Based on the class session(s) {session} and key concepts {concepts}, generate exactly {batch} questions.

Generation Guideline:
1. Generate an appropriate input to the question. The input field should contain a specific example provided for the question. It should involve realistic data and should not contain simple placeholders. The input should provide substantial content to make the question challenging.
2. Not all questions require input. For example, when a question asks about some general information, "what is the highest peak in the world", it is not necssary to provide a specific context. In this case, put "<noinput>" in the input field.
3. Balance number of questions that have input and that does not have input.
4. Questions have varying difficulty from easy, medium and hard
5. Questions are generated proportionally using Bloom's taxonomy: Remeber, Understand, Apply, Analyze and Evaluate.
6. Questions are concise with maximum of {max_tokens} tokens.
"""


generate_answer = """
Answer the question correctly and logically. Make answers short and concise.

## Question: {question}
## Input: {input}

Generation Guideline:
1. Respond "DO NOT KNOW" if not sure about the answer.
2. Answers are concise with the maximum length of {max_tokens} tokens.
"""
