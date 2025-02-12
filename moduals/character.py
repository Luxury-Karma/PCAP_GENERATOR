import re
import time
from multiprocessing.connection import answer_challenge

from moduals.AI_communication import OllamaClient,option_detection
from moduals import ssh, smtp
from moduals.smtp import instantiate_email,make_data
from paramiko import channel


def find_chosen_file(answer:str, files:list[str]) -> str:
    f: str = ''
    for e in files:
        r: str = rf'{e}'
        catch: list[str] = re.findall(e, answer)
        if catch:
            f = e
            break
    return f


class Character:
    def __init__(self,ai:OllamaClient,computer_connection:ssh.SSHClient,smtp_ip_ip:str,character_mail:str, character_os:str,
                 character_ftp_server:str, download_directory:str,upload_directory:str
                 ,character_ftp_user:str = 'anonymous', character_ftp_password:str = ''):
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
        self.download_directory: str = download_directory
        self.upload_directory: str = upload_directory

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

        ssh.send_multi_shell_command(self.ssh,all_commands, self.os)


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

    #region FTP

    def __get_ftp_files(self, file_re:str) -> {list[str],str}:
        from moduals import FTP
        cha: channel = FTP.connect_ftp_server(self)

        files: list[str] = re.findall(file_re, FTP.list_accessible_files(cha, self.os))
        ai_visual_files: str = 'Here are the only option you can choose of :\n'
        for e in files:
            ai_visual_files += f'{e}\n'

        FTP.quit_channel(cha, self.os)
        cha.close()
        return files, ai_visual_files

    def __get_chosen_file(self, ai_visual_files:str,files:list[str]) -> str:
        answer = self.ai.generate_response(f'Here are all of the files from the FTP server : {ai_visual_files}\n'
                                           f'for this answer you need to reply with the name of one of these files\n')
        print(ai_visual_files)
        file_chosen: str = find_chosen_file(answer, files)
        while file_chosen == '':
            answer = self.ai.generate_response(f'No, the file you asked does not exist : {answer}.'
                                               f'You need to answer one of these : {ai_visual_files}')
            file_chosen = find_chosen_file(answer, files)
            print(f"For some reason {self.ai.name} do not want to choose a proper file. Last answer: \n{answer}")
        return file_chosen

    def __download_file_ftp(self):
        from moduals import FTP
        file_re: str = r'\S+\.\w+'

        files, ai_visual_files = self.__get_ftp_files(file_re)

        file_chosen = self.__get_chosen_file(ai_visual_files,files)

        cha:channel = FTP.connect_ftp_server(self)
        FTP.download_file(cha, file_chosen, self.download_directory, self.os)
        print(f'The file {file_chosen} was downloaded from user : {self.ai.name}')
        FTP.quit_channel(cha, self.os)
        cha.close()

    def __get_local_files(self) -> list[str]:
        # get local file we can upload
        command = f'ls {self.upload_directory}' if self.os == 'Linux' else f'dir {self.upload_directory} /b'
        _,out = ssh.send_command_to_shell(self.ssh, command)
        return out.split('\n') if self.os == 'Linux' else [line.replace('\r', '') for line in out.split('\n')]



    def __upload_file_ftp(self):
        from moduals import FTP

        files:list[str] = self.__get_local_files()
        answer:str = self.ai.generate_response(f'Here are all the files you can choose from : {files}.What file do you whant to send to the FTP server?')
        choice: str = ''

        # I miss do while 🥲
        for e in files:
            if re.findall(e,answer):
                choice = e
                break
        #TODO use a proper output sanitiser with limitation and worst case " random " selection or something like that.
        # Actualy randomly selecting the file might be better? lets see in the future now I need to leave 😪
        while choice == '':
            answer = self.ai.generate_response(f'I told you those : {files} are the only one you can choose. You need to choose one of those. Its an order.')
            for e in files:
                if re.findall(rf'\b{re.escape(e)}\b', answer):  # Use re.escape to handle special characters
                    choice = e
                    break
        print(f'choice: {choice}')
        cha:channel =  FTP.connect_ftp_server(self)
        print(f'{self.os}')
        FTP.upload_file(cha,self.upload_directory,choice,self.os)
        print('upload successful')





    def control_ftp(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        FTP transfer are made by the AI
        :return:
        """

        self.__upload_file_ftp()

        #todo:remove after testing of upload
        return
        choice : str = self.ai.generate_response('You have chosen to download or upload a file. '
                                                'Do you want to download or upload?')

        #TODO: I am lacking time right now we need to add something to do output sanitization from the AI in a more generalise form
        if re.findall('download',choice.lower()):
            self.__download_file_ftp()
        if re.findall('upload',choice.lower()):
            self.__upload_file_ftp()

    #endregion