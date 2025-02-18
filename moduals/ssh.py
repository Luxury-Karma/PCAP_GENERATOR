# TODO : Make random connection to SSH some making as if they where bruteforcing the connection. If its a okay one do a couple random commande to just make pcap.
import time
from getopt import error

import paramiko
from paramiko.client import SSHClient
from paramiko import channel
import chardet


# region connections

def connect_to_ssh_server(ssh_server_ip: str, user_name: str, password: str, port: int = 22, timeout: int = 3) -> [
    SSHClient, bool]:
    """
    Connect the client to a SSH shell
    :param ssh_server_ip: SSH server IP
    :param user_name: SSH user name
    :param password: SSH user password
    :param port: port for ssh base : 22
    :param timeout: how long we wait for a connection base : 3 seconds
    :return: SSH connection (SSHClient) and if connection worked (bool)
    """
    ssh: SSHClient = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(
            f"trying to connect at : {ssh_server_ip}, with the user and password : {user_name}/{password} on port {port}")
        ssh.connect(hostname=ssh_server_ip, port=port, username=user_name, password=password, timeout=timeout)
        return ssh, True
    except  Exception as e:
        print(f'could not connect to ssh {e}')
        return ssh, False


def get_interactive_shell(shell: SSHClient) -> channel:
    """
    Generate a channel to communicate for longer communications
    :param shell: ssh connection
    :return: connected channel
    """
    if not shell.get_transport() or not shell.get_transport().is_active():
        # TODO : REPLACE THIS with a reconnection since we have an AI to do it.
        # The logic is that if the shell doesn't exist anymore we need to reconnect ( we might have been timed out its not impossible ) 
        raise ValueError("SSH connection is not active. Cannot open interactive shell.")

    try:
        int_shell: channel = shell.invoke_shell()
        time.sleep(1)
        return int_shell
    except paramiko.ssh_exception.ChannelException as e:
        return None




# endregion

# region Shell Control

def send_command_to_shell(shell: paramiko.SSHClient, command: str) -> (bool, str):
    stdin, stdout, stderr = shell.exec_command(command)

    exit_status = stdout.channel.recv_exit_status()
    raw_output = stdout.read()
    detected_encoding = chardet.detect(raw_output)['encoding']

    output = raw_output.decode(detected_encoding or 'utf-8', errors='replace').strip()
    error = stderr.read().decode('utf-8', errors='replace').strip()

    if exit_status == 0:
        print(f"Success: {output}")
        return True, output
    else:
        print(f"Error: {error}")
        return False, error



def send_multi_shell_command(ssh: paramiko.SSHClient, commands: list[tuple[str, str]], os: str,
                             change_os_position: int = None, changed_os: str = None) -> None:
    """
    Make a multiple command session with a channel. Use if you do not want to handle the channel yourself
    :param changed_os: to what OS do we change
    :param change_os_position: if we connect to an other OS during the command during the process
    :param os: os the user is on
    :param ssh: ssh connected
    :param commands: what commands to send with the planed output
    :return: Nothing
    """

    shell = get_interactive_shell(ssh)
    # TODO find a better way ?
    if not shell:
        print('Error Connecting to the interactive shell passing to next user')
        return
    depth: int = 0
    for cmd, wait_for in commands:
        if depth == change_os_position:
            os = changed_os
        output = send_command_interactive(shell, cmd, wait_for, os)
        print(f"Command: {cmd}\nResponse: {output}\n")
        depth += 1
    shell.close()


def send_command_interactive(int_shell: channel, command: str, wait_for: str, os: str, timeout: int = 5) -> str:
    """
    Send a single command to a channel.
    :param os: os the user is on
    :param int_shell: connected channel
    :param command: what command to send
    :param wait_for: supposed output
    :param timeout: how long we wait
    :return: output (Str)
    """

    recv_input = 1024 if os == 'Linux' else 4096
    sleep_time: float = 0.2 if os == 'Linux' else 0.5
    end_command: str = '\n' if os == 'Linux' else '\r\n'
    int_shell.send(command + end_command)
    output = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if int_shell.recv_ready():
            recv = int_shell.recv(recv_input).decode("utf-8", errors='ignore')
            output += recv
            # Check if the expected response is in the output
            if wait_for in output:
                break
        time.sleep(sleep_time)
    return output

# endregion


# TODO: Add the bruteforce thing here. We could also use Hydra command line from a kali machine that we connect through SSH?
