from moduals import ssh,http
from moduals.AI_communication import OllamaClient,get_basic_prompt,option_detection
from moduals.character import Character
from paramiko import channel

import json

def main():
    information: dict = get_all_ai_info()
    character:list[Character]=setup_all_ai(information)
    setup_next_ais_actions(character)

    for e in character:
        e.control_ftp()

    print('over')

    #email:list[str] = ["kali","other"]
    #domain_name:str = "@gotscam.com"
    #make_readable_smtp.instantiate_email(server_ip="10.0.0.14",email_list=email,amount_of_email=10,domain=domain_name,ai_communication=ai,files_directory="/home/luxurykarma/Pictures/test")

def setup_next_ais_actions(characters:list[Character]):
    for e in characters:
        e.make_decision()



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
        s,_ = ssh.connect_to_ssh_server(value['ssh_ip'],value['username'],value['password'])
        all_character.append(Character(OllamaClient(personality,key),s,'10.0.0.14',value['email'],value['os'],value['ftp_server']))
    return all_character


if __name__ == '__main__':
    main()