#TODO: Behing able to simulate a NMAP scan if wanted. making ICMP noise from a couple devices ( potentially need to use SSH who know we'll do it once there )
import subprocess
from moduals.character import Character

def ping(dest:str,ai:Character, ping_amount:int = 4):
    command: str = f'ping {dest} -c {ping_amount}'
    if ai.os != 'Linux':
        command =  f'ping {dest} -n {ping_amount}'
    ai.ssh.exec_command(command)

def tracert(dest:str, ai:Character):
    command: str = f'traceroute {dest}'
    if ai.os != 'Linux':
        command = f'tracert {dest}'
    ai.ssh.exec_command(command)

