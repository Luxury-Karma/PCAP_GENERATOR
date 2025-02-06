import ollama
import re


def option_detection(answer: str):
    answer = answer.lower()
    if re.search(r'\bwebsite\b', answer):
        print('Website detected')
        return 'website'
    elif re.search(r'\bemail\b', answer):
        print('Email detected')
        return 'email'
    elif re.search(r'\bftp\b', answer):
        print('FTP detected')
        return 'ftp'
    elif re.search(r'\bssh\b', answer):
        print('SSH connection detected')
        return 'ssh'
    else:
        print('No known option detected')
        return ''


def get_basic_prompt()->str:
    return ('You will be assisting in my automation tool. You will act as an employee of my company.'
    'You will need to tell me what is the next thing you want to do. The thing you can do is : '
    '\t-1: Go on a website'
    '\t-2: Send an email'
    '\t-3: download a file from FTP'
    '\t-4: Try an ssh connection to a server.'
    'Except if I tell you for something such as an email or an option you will only answer with your action. such as : \'website\' '
    'Now here is your personality:')


class OllamaClient:
    def __init__(self, system_message=None,ai_name:str='', model='llama3'):
        self.model:str = model
        self.system_message:str = system_message
        self.name:str= ai_name
        self.conversation_history:list[dict] = []
        if self.system_message:
            self.conversation_history.append({'role': 'system', 'content': self.system_message})

    def generate_response(self, user_input):
        self.conversation_history.append({'role': 'user', 'content': user_input})
        response = ollama.chat(model=self.model, messages=self.conversation_history, stream=False)
        assistant_reply = response['message']['content']
        self.conversation_history.append({'role': 'assistant', 'content': assistant_reply})
        return assistant_reply

