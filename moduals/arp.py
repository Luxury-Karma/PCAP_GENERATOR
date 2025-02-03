#TODO: make noise with arp request. ( Potentially trying to do arp poisoning lets see if I have time )
import subprocess
from typing import Any
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp
import socket
import re


def get_network_information() -> list[dict[str,Any]]:
    """
    Get the network information from your device and find all other device on this lan
    :return: dict[str,Any]
    """
    l_net:str = __get_lan()
    if l_net == "No match found":
        print("Error no ip was found. skipping ARP")
        return []
    return __arp_scan(l_net)


#region sending packet

def __send_arp_request(target_ip) -> dict[str, Any]:
    """
    Send a ARP request to find the mac of a specific host
    :param target_ip: ip we want to find the mac
    :return: dict[str,Any] ( dictionary with ip and mac )
    """

    arp_request = ARP(pdst=target_ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    answer:dict[str,Any] = {}
    print(f"Sending ARP request to {target_ip}...")
    # Use srp to send the packet and capture responses.
    answered, unanswered = srp(packet, timeout=2, verbose=True)

    for sent, received in answered:
         answer.update({
            'ip': target_ip,
            'mac': received.hwsrc
        })

    return answer

def __arp_scan(ip_range)-> list[dict[str,Any]]:
    """
    Make an ARP request on every possible IP in this range. Get the answer assign MAC and IP together.
    :param ip_range: Range of ip we want to scan EX : 10.0.0.0/24
    :return: list[dict[str,Any]] ( joint ip and mac address in a list of dictionary )
    """
    # Combine Ethernet frame and ARP request into a single packet.
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)

    print(f"Scanning network: {ip_range} ...")
    answered, _ = srp(packet, timeout=2, verbose=False)

    hosts = []
    for _, received in answered:
        hosts.append({'ip': received.psrc, 'mac': received.hwsrc})

    return hosts

#endregion

#region find network

def __get_lan() -> str:
    """
    Use built in command to find the network this device is on.
    :return: str : the ip with the subnet ex : 10.0.0.0/24
    """

    pattern = rf"({re.escape(socket.gethostbyname(socket.gethostname()))})\/((\d\d)|\d)"

    value:str = ''

    # Verify if the command  work
    try:
        value = subprocess.check_output("ipconfig", shell=True, text=True)
    except:
        print("ipconfig not recognise. OS not Windows base")

    try:
        value = subprocess.check_output("ip a", shell=True, text=True)
    except:
        print("ip a not recognise. Os not Linux base")

    if value == '':
        print("was not able to get IP. abandoning this part.\ncommand line error. Can not grab local ip.\nGET OUT OF MACOS")
        return 'Error finding IP'

    match = re.search(pattern, value)
    if not match:
        return "Error finding IP"
    return match.group(0)

#endregion



