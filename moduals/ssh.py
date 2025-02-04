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

def send_command_to_shell(shell:SSHClient,command:str):
    shell.exec_command(command)

#TODO: Add the bruteforce thing here. We could also use Hydra command line from a kali machine that we connect through SSH?
