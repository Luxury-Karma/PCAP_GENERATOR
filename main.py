from moduals import ssh
from moduals.AI_communication import OllamaClient,get_basic_prompt,option_detection
from moduals.character import Character

import json

def main():
    information: dict = get_all_ai_info()
    character:list[Character]=setup_all_ai(information)
    for char in character:
        message:str = char.ai.generate_response('You are sending a professional email to someone you think is an dumbass. Please write it.')
        subject:str = char.ai.generate_response(f'Make a couple word description of the conversation for the email subject. Here is the message: {message}')
        destination:str = ''
        for key, value in information.items():
            if key != char.ai.name:
                destination = value['email']
                break
        char.control_email(destination,message,subject)
    print('Communication is done')
    #email:list[str] = ["kali","other"]
    #domain_name:str = "@gotscam.com"
    #make_readable_smtp.instantiate_email(server_ip="10.0.0.14",email_list=email,amount_of_email=10,domain=domain_name,ai_communication=ai,files_directory="/home/luxurykarma/Pictures/test")

def get_all_ai_info():
    info:dict = {}
    with open('./Ai_information/contact_information.json','r') as f:
        info.update(json.load(f))
    return info

def setup_all_ai(all_ai_info:dict):
    all_character:list[Character] = []
    for key,value in all_ai_info.items():
        personality:str = get_basic_prompt()
        personality+=value['personality']
        s,_ = ssh.connect_to_ssh_server('10.0.0.14','kali','kali')
        all_character.append(Character(OllamaClient(personality,key),s,'10.0.0.14',value['email']))
    return all_character


if __name__ == '__main__':
    main()