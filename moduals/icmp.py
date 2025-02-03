#TODO: Behing able to simulate a NMAP scan if wanted. making ICMP noise from a couple devices ( potentially need to use SSH who know we'll do it once there )
import subprocess


def ping(dest:str, ping_amount:int = 4):
    try:
        subprocess.run(f'ping {dest} -c {ping_amount}', shell=True)
    except:
        print(f"was not able to ping destination {dest}")

def tracert(dest:str):
    try:
        subprocess.run(f'traceroute {dest}',shell=True)
        return
    except:
        pass
    try:
        subprocess.run(f'tracert {dest}', shell=True)
    except:
        print(f'Was not able to find a route to {dest}')

