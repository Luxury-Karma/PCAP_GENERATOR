from moduals.AI_communication import OllamaClient
from moduals.AI_communication import option_detection
from moduals import ssh
from moduals.smtp import instantiate_email,__make_data

class Character:
    def __init__(self,ai:OllamaClient,computer_connection:ssh.SSHClient,smtp_ip_ip:str,character_mail:str):
        self.ai:OllamaClient = ai
        self.ssh:ssh.SSHClient = computer_connection
        self.last_decision:str = ''
        self.smtp_ip:str = smtp_ip_ip
        self.email:str = character_mail

    def make_decision(self):
        prompt:str = 'Rolle back to your base option given at the start of the conversation.'if  self.last_decision == '' else f'Rolle back to your base option given at the start of the conversation. your last decision was : {self.last_decision}. maybe try to vary a bit?'
        decision =  option_detection(self.ai.generate_response(prompt))
        self.last_decision=decision

    def send_command(self, command:str):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdout.channel.recv_exit_status()  # Wait for command to complete
        return stdout.read().decode(), stderr.read().decode()

    def control_email(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection
        to ensure that the email was sent.
        """
        email_dest: str = f'{self.email}'  # TODO: AI should choose the email recipient
        email_subject: str = 'test'  # TODO: AI should decide the subject
        email_body: str = __make_data(self.email,self.email,email_subject,'I am a test', [])  # TODO: Ensure the body is properly formatted with smtp.py functions
        email_content = f'From: {self.email}\r\nTo: {email_dest}\r\nSubject: {email_subject}\r\n\r\n{email_body}\r\n.'

        self.send_command(f'telnet {self.smtp_ip} 25')
        self.send_command('EHLO localhost')
        self.send_command(f'MAIL FROM: {self.email}')
        self.send_command(f'RCPT TO:{email_dest}')
        self.send_command('DATA')
        self.send_command(email_content)
        self.send_command('QUIT')

        return

    def control_website(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        website is open on the local machine
        :return:
        """
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