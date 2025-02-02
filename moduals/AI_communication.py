import ollama

class OllamaClient:
    def __init__(self, model='llama3'):
        self.model = model

    def generate_text(self, prompt):
        result = ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        return result['response']

