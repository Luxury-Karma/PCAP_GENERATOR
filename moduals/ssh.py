#TODO : Make random connection to SSH some making as if they where bruteforcing the connection. If its a okay one do a couple random commande to just make pcap.
import time

import paramiko
from paramiko.client import SSHClient
from paramiko import channel

#region connections

def connect_to_ssh_server(ssh_server_ip:str,user_name:str,password:str,port:int=22,timeout:int=3)->[SSHClient,bool]:
    ssh:SSHClient = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"trying to connect at : {ssh_server_ip}, with the user and password : {user_name}/{password} on port {port}")
        ssh.connect(hostname=ssh_server_ip,port=port,username=user_name,password=password,timeout=timeout)
        return ssh,True
    except  Exception as e:
        print(f'could not connect to ssh {e}')
        return ssh, False

def get_interactive_shell(shell:SSHClient):
    int_shell:channel = shell.invoke_shell()
    time.sleep(1)
    time.sleep(1)
    return int_shell

#endregion

#region Shell Control
def send_command_to_shell(shell: paramiko.SSHClient, command: str) -> (bool,str):
    stdin, stdout, stderr = shell.exec_command(command)

    exit_status = stdout.channel.recv_exit_status()  # Get exit status
    output = stdout.read().decode().strip()  # Read standard output
    error = stderr.read().decode().strip()  # Read standard error

    if exit_status == 0:
        print(f"Success: {output}")
        return True, output  # Indicating success
    else:
        print(f"Error: {error}")
        return False, error  # Indicating failure


def send_multi_shell_command(ssh: paramiko.SSHClient, commands: list[tuple[str, str]]):
    shell = get_interactive_shell(ssh)

    for cmd, wait_for in commands:
        output = send_command_interactive(shell, cmd, wait_for, timeout=5)
        print(f"Command: {cmd}\nResponse: {output}\n")
    shell.close()


def send_command_interactive(int_shell: channel, command: str, wait_for: str, timeout: int = 5) -> str:
    int_shell.send(command + '\n')
    output = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if int_shell.recv_ready():
            recv = int_shell.recv(1024).decode("utf-8")
            output += recv
            # Check if the expected response is in the output
            if wait_for in output:
                break
        time.sleep(0.2)
    return output

#endregion


#TODO: Add the bruteforce thing here. We could also use Hydra command line from a kali machine that we connect through SSH?

