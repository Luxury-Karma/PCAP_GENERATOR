from ftplib import FTP

def connect_to_server(server_ip:str, username:str='',password:str='') -> FTP:
    ftp = FTP(host=server_ip)
    ftp.login(username,password)
    return ftp


def quit_server(ftp:FTP):
    ftp.quit()


def get_ftp_files(ftp:FTP)-> list[str]:
    """
    Give all the files from the FTP server.
    :param ftp: FTP server connection
    :return: list of files on the FTP server
    """
    return ftp.nlst()


def upload_file(ftp: FTP, local_file_path: str, remote_file_path: str):
    """
    Uploads a file to the FTP server.

    :param ftp: An active FTP connection object.
    :param local_file_path: Path to the local file to be uploaded.
    :param remote_file_path: Path on the FTP server where the file will be stored.
    """
    with open(local_file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_file_path}', file)
    print(f"Uploaded {local_file_path} to {remote_file_path}")


def download_file(ftp: FTP, remote_file_path: str, local_file_path: str):
    """
    Downloads a file from the FTP server.
    :param ftp: An active FTP connection object.
    :param remote_file_path: Path to the file on the FTP server to be downloaded.
    :param local_file_path: Path where the downloaded file will be saved locally.
    """
    with open(local_file_path, 'wb') as file:
        ftp.retrbinary(f'RETR {remote_file_path}', file.write)
    print(f"Downloaded {remote_file_path} to {local_file_path}")
