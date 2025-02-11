from moduals.character import Character
from moduals.ssh import get_interactive_shell, send_command_interactive
from paramiko import channel
import re


# TODO: Prepare character to have a FTP credential so we can follow them and their download. and maybe spot a wrong user

def connect_ftp_server(ai:Character) -> channel:
    """
    Connect the interactive channel to the FTP server for the AI.
    :param ai: Character used.
    :param server_ip: Where is the FTP server
    :param user_name: Username on FTP server
    :param password: Password for that user
    :return: channel connected to the server
    """
    cha: channel = get_interactive_shell(ai.ssh)
    command:list[list[str]] = [
        [f'ftp {ai.ftp_server}', '220'],
        [f'{ai.ftp_user}', '331'],
        [f'{ai.ftp_pass}', '230'],
    ]

    for e in command:
        print(send_command_interactive(cha, e[0], e[1]))

    return cha


def list_accessible_files(cha:channel) -> str:
    """
    get all the accessible files from the FTP server
    :param cha: interactive Channel
    :return: list of the server's file
    """
    return send_command_interactive(cha,'ls','226')


def upload_file(cha:channel, file_to_upload:str) -> None:
    """
    Send a local file to the FTP server
    :param cha: interactive channel
    :param file_to_upload: full path of the file to upload
    :return: Nothing
    """
    reg_detection:str = r'^(.*[\\/])'
    directory:str = re.match(reg_detection,file_to_upload).groups()[0]
    file_name:str = file_to_upload.strip(directory)
    commands:list[list[str]] = [
        [f'lcd {directory}', 'Local directory' ],
        [f'put {file_name}', '226']
    ]
    for e in commands:
        send_command_interactive(cha,e[0],e[1])


def download_file(cha:channel, file_to_download:str, local_path:str) -> None:
    """
    Get a file from the FTP server
    :param cha: interactive channel
    :param file_to_download: file name to download
    :param local_path: where to put the file
    :return: none
    """
    send_command_interactive(cha,f'get {file_to_download} {f'{local_path}\\{file_to_download}'}', '226')


def quit_channel(cha:channel)->None:
    send_command_interactive(cha,'bye','221')
