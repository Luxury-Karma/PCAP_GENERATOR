# Training_pcap_maker
A noise maker for pcap based on Ollama.

# How does it work ? 
The script connect to the VM by SSH. The scripts then use Ollama client with an Ai model run on it
Each individual user can be set with different persona and will do choice base on them to make noise on the network.
The script can work with windows and linux machine.

# What is the minimal setup? 
The minimal setup is one linux machine with postfix, FTP and one user on the machine.
Linux (for now) is required since the telnet connection have problem passing through SSH when we are on windows and the script
work in a way where we use telnet for email to simplify reading and seeing them.
I would recommend to pass all network by your host, so you can run wireshark only on your host and receive all PCAP from 
all the VM

# What would be a recommended configuration?
The recommended. usage is 3 to 4 machines to make a network of a couples' user.
1 Should be a Linux machine running Postfix, Windows Server running a FTP and a DC and one Windows user.
I would recommend as many user as your machine can handle VM to add more information to your network.


# Why should I use this? 
To make larger network traffic without needing to do it yourself or to add noise to exploit to practice larger scale pcap 
analysis 