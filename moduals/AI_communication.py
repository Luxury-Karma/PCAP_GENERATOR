import ollama
import re
from random import randint

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
    return ('Keep in mind the personality. Now this is your pourpus. You are a tool to assist me into '
            'automating networking traffic. When I ask a question you NEED to answer in the way I tell you. '
            'If I ask for a name you answer a name. If I ask for a number you answer a number.'
            'understood? good. We will start soon.'
            'Keep in mind when I ask a question do not create something there is not in the option. Else you are breaking your rules.')


class OllamaClient:
    def __init__(self, system_message=None,ai_name:str='', model='llama3'):
        self.model:str = model
        self.system_message:str = system_message
        self.name:str= ai_name
        self.conversation_history:list[dict] = []
        if self.system_message:
            self.conversation_history.append({'role': 'system', 'content': self.system_message})

    def generate_response(self, user_input:str, answer_choices:list[str]|None = None, maximum_attempts:int = 3) -> str:
        self.conversation_history.append({'role': 'user', 'content': user_input})
        response = ollama.chat(model=self.model, messages=self.conversation_history, stream=False)
        assistant_reply: str = response['message']['content']
        self.conversation_history.append({'role': 'assistant', 'content': assistant_reply})
        if not answer_choices:
            return assistant_reply
        is_random:bool = True
        for i in range(maximum_attempts):
            self.conversation_history.append({'role': 'user', 'content': f'Your answer is wrong. Your only options where : {answer_choices}. If you do not choose I will choose for you. What do you want in those options.'})
            assistant_reply = ollama.chat(model=self.model, messages=self.conversation_history, stream=False)['message']['content']
            for e in assistant_reply:
                if e not in response:
                    continue
                assistant_reply = e
                is_random = False
                break
            if is_random:
               assistant_reply =  answer_choices[randint(0,len(answer_choices)-1)]


        self.conversation_history.append({'role': 'assistant', 'content': assistant_reply})
        return assistant_reply