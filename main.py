from moduals import ssh
from moduals.AI_communication import OllamaClient,get_basic_prompt,option_detection
from moduals.character import Character

def main():
    personality:str = get_basic_prompt()
    personality+= ('You are Bob a salty employee waiting to loose his job. Doing the least amount of work is your goal.'
                   'You are still somewhat reliable on some task and will not act against the company willingly.')
    t:OllamaClient = OllamaClient(personality)
    s,_ = ssh.connect_to_ssh_server('10.0.0.14','kali','kali')
    c:Character = Character(t,s,'10.0.0.14','kali@gotscam.com')
    c.control_email()


    #email:list[str] = ["kali","other"]
    #domain_name:str = "@gotscam.com"
    #make_readable_smtp.instantiate_email(server_ip="10.0.0.14",email_list=email,amount_of_email=10,domain=domain_name,ai_communication=ai,files_directory="/home/luxurykarma/Pictures/test")




if __name__ == '__main__':
    main()