from moduals.character import Character
from moduals.ssh import get_interactive_shell, send_command_interactive
from paramiko import channel


# TODO: Prepare character to have a FTP credential so we can follow them and their download. and maybe spot a wrong user



def list_accessible_files(cha:channel, os:str) -> str:
    """
    get all the accessible files from the FTP server
    :param os: What os is the machine base on
    :param cha: interactive Channel
    :return: list of the server's file
    """
    return send_command_interactive(cha,'ls','226', os)


def upload_file(cha:channel, file_directory:str, file_name:str, os:str) -> None:
    """
    Send a local file to the FTP server
    :param os: What are we running the command into
    :param file_name: the name of the uploaded file
    :param file_directory: Where is the file
    :param cha: interactive channel
    :return: Nothing
    """
    commands:list[list[str]] = [
        ['binary','200'],
        [f'lcd "{file_directory}"', 'Local directory' ],
        [f'put "{file_name}"', '226']
    ]
    for e in commands:
        send_command_interactive(cha,e[0],e[1], os)


def download_file(cha:channel, file_to_download:str, local_path:str, os:str) -> None:
    """
    Get a file from the FTP server
    :param os: Os of the system user
    :param cha: interactive channel
    :param file_to_download: file name to download
    :param local_path: where to put the file
    :return: none
    """
    send_command_interactive(cha,f'binary','200',os)
    send_command_interactive(cha,f'get {file_to_download} {f'{local_path}\\{file_to_download}'}', '226', os)


#region Connection

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
        send_command_interactive(cha, e[0], e[1], ai.os)

    return cha


def quit_channel(cha:channel, os:str)->None:
    send_command_interactive(cha,'bye','221', os)

#endregion