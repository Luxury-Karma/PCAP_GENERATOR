from ftplib import FTP
from moduals.character import Character
from moduals.ssh import get_interactive_shell, send_command_interactive

# TODO: refactor for AI and SSH usage.

def connect_to_server(server_ip:str,ai:Character, username:str='',password:str=''):
    int_shell:

def quit_server(ftp:FTP):
    pass


def get_ftp_files(ftp:FTP)-> list[str]:
    pass


def upload_file(ftp: FTP, local_file_path: str, remote_file_path: str):
    pass


def download_file(ftp: FTP, remote_file_path: str, local_file_path: str):
    pass
