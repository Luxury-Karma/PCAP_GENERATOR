import ollama

class OllamaClient:
    def __init__(self, model='llama3'):
        self.model = model

    def chat(self, user_message):
        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': user_message}]
        )
        return response['message']['content']

    def generate_text(self, prompt):
        result = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        return result['response']

