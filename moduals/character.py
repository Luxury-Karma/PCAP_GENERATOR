import json
import random
import re
from calendar import prmonth

from moduals.AI_communication import OllamaClient, option_detection
from moduals import smtp
from moduals.ssh import send_multi_shell_command, send_command_to_shell, get_interactive_shell, send_command_interactive
from paramiko.client import SSHClient
from paramiko import channel
import datetime
import csv
import os
from moduals import FTP


def find_chosen_file(answer: str, files: list[str]) -> str:
    f: str = ''
    i:int = 1
    for e in files:
        r: str = rf'{e}'

        if e in answer or str(i) in answer:
            f = e
            break
        i += 1
    return f


class Character:
    def __init__(self, ai: OllamaClient, computer_connection: SSHClient, smtp_ip_ip: str, character_mail: str,
                 character_os: str,
                 character_ftp_server: str, download_directory: str, upload_directory: str, ssh_access:dict
                 , character_ftp_user: str = 'anonymous', character_ftp_password: str = ''):
        """
        Each net user with their action and all the information we need to make them work
        :param ai: the Llama persona
        :param computer_connection: the SSH connection to the computer
        :param smtp_ip_ip: Where is the mail server
        :param character_mail: what is the user email
        :param character_os: What os is the user using ( mostly use for commands ) (options : Windows, Windows Server, Linux)
        """
        self.ai: OllamaClient = ai
        self.ssh: SSHClient = computer_connection
        self.last_decision: str = ''
        self.smtp_ip: str = smtp_ip_ip
        self.email: str = character_mail
        self.os: str = character_os
        self.ftp_server: str = character_ftp_server
        self.ftp_user: str = character_ftp_user
        self.ftp_pass: str = character_ftp_password
        self.download_directory: str = download_directory
        self.upload_directory: str = upload_directory
        self.ssh_access:dict = ssh_access

    def make_decision(self):
        option = ['website', 'email', 'FTP'] if self.ssh_access == {} else ['website', 'email', 'FTP', 'SSH']



        prompt: str = 'We get a new decision. Right now your options are : '

        for e in option:
            prompt += prompt + f'\n {e}'

        prompt = prompt + ('You need to choose the option and tell me the full name for detection.\n'
                       f'also for your knowledge your last decision was : {self.last_decision}. Try to be imaginative !')

        decision = option_detection(self.ai.generate_response(prompt,option))
        self.last_decision = decision
        if decision == 'website':
            self.control_website()
        elif decision == 'email':
            self.control_email()
        elif decision == 'ftp':
            self.control_ftp()
        elif decision == 'ssh':
            self.control_ssh()
        else:
            print("didn't choose anything")

    #region email
    # TODO: send the information to the next AI so it can know what happened

    def send_email(self, destination: str, subject: str, email_body: str) -> None:
        email_content: str = f'From: {self.email}\r\nTo: {destination}\r\nSubject: {subject}\r\n\r\n{email_body}\r\n.'

        if self.os != 'Linux':
            all_commands: list[tuple[str, str]] = [
                (f'ssh kali@{self.smtp_ip}', 'password'),
                # (f'yes','password'),
                (f'kali', 'Last login'),
                (f'telnet {self.smtp_ip} 25', "220"),
                ("EHLO localhost", "250"),
                (f'MAIL FROM: {self.email}', "250"),
                (f'RCPT TO:{destination}', "250"),
                ("DATA", "354"),
                (email_content, "250"),
                ("QUIT", "221")
            ]
            send_multi_shell_command(self.ssh, all_commands, self.os, 2, 'Linux')
            self.log_user_action('SENT MAIL', 'TEMP',
                                 f'User({self.ai.name} sent an email with title {subject} to user {destination} with the SMTP server at address : {self.smtp_ip}')
            return

        all_commands: list[tuple[str, str]] = [
            (f'telnet {self.smtp_ip} 25', "220"),
            ("EHLO localhost", "250"),
            (f'MAIL FROM: {self.email}', "250"),
            (f'RCPT TO:{destination}', "250"),
            ("DATA", "354"),
            (email_content, "250"),
            ("QUIT", "221")
        ]

        send_multi_shell_command(self.ssh, all_commands, self.os)
        return

    def control_email(self) -> dict:
        # TODO: Temporary solution for Windows, The telnet is kinda broken for automation so we will make a SSH
        #  connection from the host to the linux server then the linux server make the telnet move. That should solve
        #  the problem
        """
        Give option to the AI and then send the command to the machine through the SSH connection
        to ensure that the email was sent.
        """

        email_list: dict = {}
        with open('./Ai_information/all_email.json', 'r') as em:
            email_list.update(json.load(em))

        answer: str = self.ai.generate_response(
            f'You have choose to send en email. here is the list of user : {email_list}.'
            f'You need to choose one of them. Use the name on the left. Do not send an email to your self you are :{self.ai.name}.')

        destination: str = ''

        for key, value in email_list.items():
            if re.findall(key.lower(), answer.lower()) or re.findall(answer.lower(), value.lower()):
                destination = value
                break
        message: str = self.ai.generate_response(
            f'You are sending an email to {destination}. what do you want to write in the email as the message? Do a '
            f'rolleplay so return only the message.')
        subject: str = self.ai.generate_response(
            f'You are sending this email {message} to {destination}. You need to find a subject. The subject should '
            f'be a short phrase of a couple words maximum. You are rollplaying so just tell me exactly what the '
            f'subject is.')

        # Todo: Add more logic to be more in match with the communication if possible
        files_to_add: list[str] = []
        if smtp.is_download_file():
            get_files: list[str] = self.__get_local_files()
            files_to_add.append(get_files[random.randint(0, len(get_files) - 1)])

        email_body: str = smtp.make_data(self.email, destination, subject, message,
                                         [])  # TODO: Ensure the body is properly formatted with smtp.py functions

        self.send_email(destination, subject, email_body)

        return {
            'dest': self.email,
            'mail': email_body
        }

    # TODO: send order to the received AI to answer from outside once its done.
    def email_reception(self, email_received: str):
        email_from: str = re.findall(r'From:\s(\S+@\S+\.[^\\r]+)', email_received)[
            0]  # TODO ensure that the \\r is not a \r insted.
        subject: str = re.findall(r'(Subject:\s)+(.*?)(?=\\r\\n)', email_received)[0]  # TODO same as above
        email_body: str = re.findall(r'(\\r\\n\\r\\n)(.*?)(?=\\r\\n\.)', email_received)[0]  # TODO : +1

        answer: str = self.ai.generate_response(
            f'You have received an email from {email_from}. The subject is : {subject}.'
            f'The information in the email is this : {email_body}.'
            f'You will answer this email. You do not need to give me a subject or any other '
            f'information than what will be in the email'
            f'You will give me ONLY the information you will answer. Please give me the answer.')

        email_content: str = f'From: {self.email}\r\nTo: {email_from}\r\nSubject: re:{subject}\r\n\r\n{answer}\r\n.'

        self.send_email(email_from, self.email, email_content)
    #endregion

    # region website

    def curl_website(self, domain_name: str) -> str:
        _, curl = send_command_to_shell(self.ssh, f'curl {domain_name}')
        self.log_user_action('CURL WEB BROWSER','TEMP',f'The user {self.ai.name} went on the website: {domain_name}')
        return curl

    # TODO : we need to find a way to start process with the web browser
    # We could do with a bash and ps1 script to do it. We would need admin access tho.
    def open_website(self, domain_name: str) -> None or channel:
        pass


    def control_website(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        website is open on the local machine
        :return:
        """
        website_options:dict[str:dict[str:str]]
        with open('./Ai_information/webpages.json', 'r') as f:
            website_options = json.load(f)
        format_website_ai:str = ''
        i:int = 1
        for key in website_options.keys() :
            format_website_ai += format_website_ai + f'\n - {i}: website name : {key}, Website usage : {website_options[key]['explanation']}'


        answer:str = self.ai.generate_response(f'You have chosen to open a website. Here are your options : {format_website_ai}\n'
                                  f'You need to tell me the full website name exactly as written in your options.')
        website:str = ''
        answer = answer.lower()
        for key in website_options.keys():
            if not re.findall(rf'{key}'.lower(), answer):
                continue
            website = key
            break
        # TODO find a way to start a web browser on the machine and potentially use automated tool to make them do actions.
        self.curl_website(website_options[website]['url'])





        # Windows commands to launch website from browser : $<variable> = start-process "WEBSITE" -Passthru
        # to stop : stop-process -Id $proc.Id
        # Else we can use : curl + webpage to go on the webpage on both OS
        # On linux we can launch something like : tmux to launch a browser or : google-chrome-stable https:/www.youtube.com
        pass

    # endregion

    #region SSH

    def control_ssh(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        SSH connection is made by the user.
        :return:
        """

        prompt:str = 'Your options for SSH connection are : \n'
        i:int  = 1
        for key in self.ssh_access.keys():
            prompt = prompt + f' - {i}: {key}'

        prompt = prompt + 'Tell me EXACTLY what ip you want to connect too.'
        answer:str = self.ai.generate_response(prompt)
        choice:str = ''
        for key in self.ssh_access.keys():
            if not key in answer:
                continue
            choice = key
            break
        all_commands: list[tuple[str, str]] = [
            (f'ssh {self.ssh_access[choice]["user"]}@{choice}', 'password'),
            #(f'yes','password'),
            (f'{self.ssh_access[choice]["password"]}', 'Last login') if self.ssh_access[choice]['os'] == 'Linux' else (f'{self.ssh_access[choice]["password"]}', '(c) Microsoft Corporation. All rights reserved.'),
        ]
        send_multi_shell_command(self.ssh,all_commands, self.ssh_access[choice]["os"])

        self.log_user_action("SSH CONNECTION", "TEMP",f" User {self.ai.name} have connected with SSH to host : {choice} with username/password : {self.ssh_access[choice]['user']}/{self.ssh_access[choice]['password']}")




    #regionend

    # region FTP

    def connect_ftp_server(self) -> channel:
        """
        Connect the interactive channel to the FTP server for the AI.
        :return: channel connected to the server
        """
        cha: channel = get_interactive_shell(self.ssh)
        command: list[list[str]] = [
            [f'ftp {self.ftp_server}', '220'],
            [f'{self.ftp_user}', '331'],
            [f'{self.ftp_pass}', '230'],
        ]
        for e in command:
            send_command_interactive(cha, e[0], e[1], self.os)

        return cha

    def __get_ftp_files(self, file_re: str) -> {list[str], str}:
        from moduals import FTP
        cha: channel = self.connect_ftp_server()

        files: list[str] = re.findall(file_re, FTP.list_accessible_files(cha, self.os))
        ai_visual_files: str = 'Here are the only option you can choose of :\n'
        for e in files:
            ai_visual_files += f'{e}\n'

        FTP.quit_channel(cha, self.os)
        cha.close()
        return files, ai_visual_files

    def __get_chosen_file(self, ai_visual_files: str, files: list[str]) -> str:
        return self.ai.generate_response(f'Here are all of the files from the FTP server : {ai_visual_files}\n'
                                           f'for this answer you need to reply with the name of one of these files\n',files)

    def __download_file_ftp(self) -> str:
        from moduals import FTP
        file_re: str = r'\S+\.\w+'

        files, ai_visual_files = self.__get_ftp_files(file_re)

        choice = self.__get_chosen_file(ai_visual_files, files)

        cha: channel = self.connect_ftp_server()
        FTP.download_file(cha, choice, self.download_directory, self.os)
        print(f'The file {choice} was downloaded from user : {self.ai.name}')
        FTP.quit_channel(cha, self.os)
        cha.close()
        return choice

    def __get_local_files(self) -> list[str]:
        # get local file we can upload
        command = f'ls {self.upload_directory}' if self.os == 'Linux' else f'dir {self.upload_directory} /b'
        _, out = send_command_to_shell(self.ssh, command)
        return out.split('\n') if self.os == 'Linux' else [line.replace('\r', '') for line in out.split('\n')]

    def __upload_file_ftp(self) -> str:
        from moduals import FTP

        files: list[str] = self.__get_local_files()
        answer: str = self.ai.generate_response(
            f'Here are all the files you can choose from : {files}.What file do you whant to send to the FTP server?',files)

        cha: channel = self.connect_ftp_server()
        FTP.upload_file(cha, self.upload_directory, answer, self.os)
        FTP.quit_channel(cha, self.os)
        cha.close()
        return answer

    def control_ftp(self):
        """
        Give option to the AI and then send the command to the machine through the SSH connection to ensure that the
        FTP transfer are made by the AI
        :return:
        """
        answer: str = self.ai.generate_response(
            'You have chosen to transfer FTP file ( either download or upload ). Do you wish to download'
            'or upload? those two are the only choice you can choose.', ['upload', 'download'])

        #file: str = self.__download_file_ftp()
        file: str = self.__upload_file_ftp() if re.findall('upload', answer) else self.__download_file_ftp()
        self.log_user_action('UPLOAD FTP' if re.findall('upload', answer) else 'DOWNLOAD FTP', 'TEMP',
                             f'The user({self.ai.name}) uploaded the file {file}' if re.findall('upload', answer)
                             else f'The user({self.ai.name}) Downloaded the file {file}')

    # endregion

    # region logs

    def log_user_action(self, action_title: str, status: str, details: str):
        log_path: str = './log/log.csv'
        with open(log_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not os.path.exists(log_path):
                writer.writerow("Timestamp", "AI Name", "Action", "Status", "Details")
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.ai.name,
                action_title,
                status,
                details
            ])

        pass

    # endregion
