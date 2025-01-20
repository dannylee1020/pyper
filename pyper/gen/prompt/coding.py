generate_question = """
Based on the class session(s) {session} and key concepts {concepts}, generate exactly {batch} questions.
All of the questions should ask to write code in various languages (Python, Javascript, Go, Java, C++, C, and Rust). The questions should focus on implementation adn practical knowledge of programming, not theoretical concepts.

Generation Guideline:
1. Generate an appropriate input to the question. The input field should contain a specific example provided for the question. It should involve realistic data and should not contain simple placeholders. The input should provide substantial content to make the question challenging.
2. Not all questions require input. For example, when a question asks about some general information, "what is the highest peak in the world", it is not necssary to provide a specific context. In this case, put "<noinput>" in the input field.
3. Questions should be generated evenly with and without the input.
4. Questions have varying difficulty from easy, medium and hard
5. Questions should be generated evenly across different languages.
6. Questions are concise with maximum of {max_tokens} tokens.

Only generate characters that are not JSON control characters (\u0000-\u001F).
"""
