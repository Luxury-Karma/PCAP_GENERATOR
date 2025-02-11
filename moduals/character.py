import re

from moduals.AI_communication import OllamaClient,option_detection
from moduals import ssh, smtp
from moduals.smtp import instantiate_email,make_data
from paramiko import channel

class Character:
    def __init__(self,ai:OllamaClient,computer_connection:ssh.SSHClient,smtp_ip_ip:str,character_mail:str, character_os:str,
                 character_ftp_server:str, character_ftp_user:str = 'anonymous', character_ftp_password:str = ''):
        """
        Each net user with their action and all the information we need to make them work
        :param ai: the Llama persona
        :param computer_connection: the SSH connection to the computer
        :param smtp_ip_ip: Where is the mail server
        :param character_mail: what is the user email
        :param character_os: What os is the user using ( mostly use for commands ) (options : Windows, Windows Server, Linux)
        """
        self.ai:OllamaClient = ai
        self.ssh:ssh.SSHClient = computer_connection
        self.last_decision:str = ''
        self.smtp_ip:str = smtp_ip_ip
        self.email:str = character_mail
        self.os:str = character_os
        self.ftp_server:str = character_ftp_server
        self.ftp_user: str = character_ftp_user
        self.ftp_pass: str = character_ftp_password

    def make_decision(self) :
        prompt:str = 'Rolle back to your base option given at the start of the conversation.'if  self.last_decision == '' else f'Rolle back to your base option given at the start of the conversation. your last decision was : {self.last_decision}. maybe try to vary a bit?'
        decision =  option_detection(self.ai.generate_response(prompt))
        self.last_decision=decision


    def control_email(self,destination:str, message:str, subject:str):
        """
        Give option to the AI and then send the command to the machine through the SSH connection
        to ensure that the email was sent.
        """
        email_body: str = smtp.make_data(self.email,destination,subject, message, [])  # TODO: Ensure the body is properly formatted with smtp.py functions
        email_content:str = f'From: {self.email}\r\nTo: {destination}\r\nSubject: {subject}\r\n\r\n{email_body}\r\n.'

        all_commands:list[tuple[str, str]] = [
            (f'telnet {self.smtp_ip} 25', "220"),
            ("EHLO localhost", "250"),
            (f'MAIL FROM: {self.email}', "250"),
            (f'RCPT TO:{destination}', "250"),
            ("DATA", "354"),
            (email_content, "250"),
            ("QUIT", "221")
        ]

        ssh.send_multi_shell_command(self.ssh,all_commands)


        return

    def control_website(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        website is open on the local machine
        :return:
        """

        # Windows commands to launch website from browser : $<variable> = start-process "WEBSITE" -Passthru
        # to stop : stop-process -Id $proc.Id
        # Else we can use : curl + webpage to go on the webpage on both OS
        # On linux we can launch something like : tmux to launch a browser or : google-chrome-stable https:/www.youtube.com
        pass

    def control_ssh(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        SSH connection is made by the user.
        :return:
        """
        pass

    def control_ftp(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        FTP transfer are made by the AI
        :return:
        """
        from moduals import FTP
        file_re:str = r'\S+\.\w+'

        cha:channel = FTP.connect_ftp_server(self)
        files:list[str] = re.findall(file_re,FTP.list_accessible_files(cha))
        FTP.quit_channel(cha)
        cha.close()
        answer = self.ai.generate_response(f'Here are all of the files from the FTP server : {files}.\n'
                                           f'for this answer you need to repply with the name of the file you will download.')
        print(f'files chosen : {answer}\nFrom AI: {self.ai.name}')