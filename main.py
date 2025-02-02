from moduals import make_readable_smtp
from moduals import AI_communication

def main():
    ai = AI_communication.OllamaClient()
    email:list[str] = ["kali","other"]
    domain_name:str = "@gotscam.com"
    make_readable_smtp.instantiate_email(server_ip="10.0.0.14",email_list=email,amount_of_email=10,domain=domain_name,ai_communication=ai,files_directory="/home/luxurykarma/Pictures/test")


if __name__ == '__main__':
    main()