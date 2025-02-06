from moduals.AI_communication import OllamaClient,option_detection
from moduals import ssh, smtp
from moduals.smtp import instantiate_email,make_data

class Character:
    def __init__(self,ai:OllamaClient,computer_connection:ssh.SSHClient,smtp_ip_ip:str,character_mail:str):
        self.ai:OllamaClient = ai
        self.ssh:ssh.SSHClient = computer_connection
        self.last_decision:str = ''
        self.smtp_ip:str = smtp_ip_ip
        self.email:str = character_mail

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
        pass