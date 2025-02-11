#region imports
import asyncio
import telnetlib3
import re
import base64
import os
import random
from moduals.AI_communication import OllamaClient
#endregion


#region formating files for email

def __add_file_to_data(files_info:dict):
    return f"""
    Content-Type: {files_info["content_type"]}; name=\"{files_info["f_name"]}\"
    Content-Transfer-Encoding:{files_info["f_encoding"]}
    Content-Disposition: attachment; filename=\"{files_info["f_name"]}\"
    
    
    {files_info["f_data"]}
"""

def __file_to_base64_string(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def __format_joint_file(file_path:str)->dict:
    file_name_reg:str = "[^\\/]+$"
    file_name: str = re.search(file_name_reg,file_path).group(0)

    file_information:dict = {
        "f_name":file_name,
        "f_encoding":"base64",
        "f_data": __file_to_base64_string(file_path),
        "content_type": re.search('[^.]+$',file_name).group(0)
    }
    return file_information

#endregion

#region format email
def __add_text_to_data(text_sent: str):
    return f"""
    Content-Type: text/plain; charset=\"UTF-8\"
    Content-Transfer-Encoding: 7bit

    {text_sent}
"""

def __add_header_to_data(user_from:str, user_to:str,subject:str, boundary_word:str,content_type:str="multipart/mixed"):
    return f"""
    FROM: {user_from}
    TO:{user_to}
    SUBJECT:{subject}
    MIME-VERSION: 1.0
    Content-type: {content_type}; boundary={boundary_word}
    """

def make_data(user_from:str, user_to:str, subject:str, text_message:str, files_to_join:list[str], boundary_word:str="BOUNDARY")->str:

    mail:str = ""
    #ensuring every email have their proper header
    boundary_format:str = f"\n--{boundary_word}"
    mail += __add_header_to_data(user_from,user_to,subject,boundary_word)
    mail += boundary_format

    # add the text to the email
    mail +=__add_text_to_data(text_message)
    mail += boundary_format

    # add the joint pieces to the email
    for e in files_to_join:
        if not os.path.isfile(e):
            continue
        mail += __add_file_to_data(__format_joint_file(e))
        mail += boundary_format


    return mail

#endregion

#region network communication for email

async def __send_email(server_ip:str,sender:str,recipient:str,subject:str, message:str, files_to_join:list[str], server_port:int=25) -> None:
    # SMTP server details
    smtp_server = server_ip
    port = server_port

    body = make_data(user_to=recipient,user_from=sender,subject=subject,text_message=message,
          files_to_join=files_to_join)

    # Establish a Telnet connection to the SMTP server
    reader, writer = await telnetlib3.open_connection(smtp_server, port)

    # Read the server's initial response
    response = await reader.readuntil(b'220')
    print(f"Connected to server:\n{response.decode('utf-8')}")

    # Send EHLO command
    await __send_command(writer, reader, 'EHLO localhost', b'250')

    # Specify the sender
    await __send_command(writer, reader, f'MAIL FROM:<{sender}>', b'250')

    # Specify the recipient
    await __send_command(writer, reader, f'RCPT TO:<{recipient}>', b'250')


    # Send the DATA command to begin the message body
    await __send_command(writer, reader, 'DATA', b'354')
    # Send the email headers and body
    email_content = f'From: {sender}\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{body}\r\n.'
    await __send_command(writer, reader, email_content, b'250')

    # Close the connection
    await __send_command(writer, reader, 'QUIT', b'221')

    writer.close()

    print('Email sent successfully.')

async def __send_command(writer, reader, command, expected_response_start):
    """
    Sends a command to the SMTP server and prints the response.

    :param writer: The Telnet writer stream.
    :param reader: The Telnet reader stream.
    :param command: The command string to send.
    :param expected_response_start: The expected start of the server's response (as a bytes object).
    """
    writer.write(command + '\r\n')
    response = await reader.readuntil(expected_response_start)
    print(f"Sent: {command}\nReceived: {response.decode('utf-8')}")

#endregion

#region get all information

def __get_path_to_accessible_files(path:str)->list[str]:
    if not os.path.exists(path):
        print("Wrong file path was given")
        return [""]
    all_path:list[str]= [""]
    for e in os.listdir(path):
        all_path.append(f'{path}/{e}')
    return all_path

#endregion

#region random

def __do_we_put_joint_file()->bool:
    return True if random.randint(0,1) < 1 else False

def __get_random_file(list_of_files:list[str])->list[str]:
    # TODO make something to have a possibility to have more than one files link
    return [list_of_files[random.randint(0,len(list_of_files)-1)]]

#endregion

#region accessible functions

def instantiate_email(server_ip:str, email_from:str,email_to:str, email_text_information:str,email_title:str, file_to_send_path:str):
    # Run the asyncio event loop

    print("starting new email")
    sender = email_from
    receiver = email_to
    message:str = email_text_information
    subject:str = email_title

    asyncio.run(__send_email(server_ip=server_ip,sender=sender,recipient=receiver,subject=subject,message=message, files_to_join=[file_to_send_path]
))
    print("all asked email where sent")

#endregion