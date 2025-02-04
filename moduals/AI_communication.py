import ollama

class OllamaClient:
    def __init__(self, system_message=None, model='llama3'):
        self.model = model
        self.system_message = system_message
        self.conversation_history = []
        if self.system_message:
            self.conversation_history.append({'role': 'system', 'content': self.system_message})

    def generate_response(self, user_input):
        self.conversation_history.append({'role': 'user', 'content': user_input})
        response = ollama.chat(model=self.model, messages=self.conversation_history, stream=False)
        assistant_reply = response['message']['content']
        self.conversation_history.append({'role': 'assistant', 'content': assistant_reply})
        return assistant_reply
