from paramiko.client import SSHClient
from paramiko import channel
from moduals import ssh
from moduals.ssh import send_command_interactive
from moduals.character import Character

#TODO we will add a bash or powershell script on each device to solve the problem of youtube video and thing like that.
# This will be the most time effective way of solving this problem

def curl_website(domain_name:str, ssh_connection:SSHClient) -> str:
    _, curl = ssh.send_command_to_shell(ssh_connection,f'curl {domain_name}')
    return curl

def open_website(domain_name:str, character:Character ) -> None or channel:
    if character.os != 'Linux':
        curl_website(domain_name,character.ssh)
        print('windows')
        return
    curl_website(domain_name, character.ssh)
    return
    # TODO : We need to find a bether solution than this to open web broswer on the forein host.
    # What we could do is give them all a bash script that we can control from outside but launch their basic web broswer and go where we tell it.
    shell:channel = ssh.get_interactive_shell(shell=character.ssh)
    send_command_interactive(shell,f'firefox --headless {domain_name}','*** You are running in headless mode.')  # linux
    return shell



