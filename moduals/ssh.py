#TODO : Make random connection to SSH some making as if they where bruteforcing the connection. If its a okay one do a couple random commande to just make pcap.
import paramiko
from paramiko.client import SSHClient


def connect_to_ssh_server(ssh_server_ip:str,user_name:str,password:str,port:int=22,timeout:int=3)->[SSHClient,bool]:
    ssh:SSHClient = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ssh_server_ip,port=port,username=user_name,password=password,timeout=timeout)
        return ssh,True
    except:
        return ssh, False


def send_command_to_shell(shell: paramiko.SSHClient, command: str):
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


#TODO: Add the bruteforce thing here. We could also use Hydra command line from a kali machine that we connect through SSH?

