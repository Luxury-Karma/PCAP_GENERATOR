# region imports

import re
import base64
import os


# endregion


# region formatting files for email

def __add_file_to_data(files_info: dict):
    return f"""
    Content-Type: {files_info["content_type"]}; name=\"{files_info["f_name"]}\"
    Content-Transfer-Encoding:{files_info["f_encoding"]}
    Content-Disposition: attachment; filename=\"{files_info["f_name"]}\"
    
    
    {files_info["f_data"]}
"""


def __file_to_base64_string(file_path: str) -> str:
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def __format_joint_file(file_path: str) -> dict:
    file_name_reg: str = "[^\\/]+$"
    file_name: str = re.search(file_name_reg, file_path).group(0)

    file_information: dict = {
        "f_name": file_name,
        "f_encoding": "base64",
        "f_data": __file_to_base64_string(file_path),
        "content_type": re.search('[^.]+$', file_name).group(0)
    }
    return file_information


# endregion

# region format email
def __add_text_to_data(text_sent: str):
    return f"""
    Content-Type: text/plain; charset=\"UTF-8\"
    Content-Transfer-Encoding: 7bit

    {text_sent}
"""


def __add_header_to_data(user_from: str, user_to: str, subject: str, boundary_word: str,
                         content_type: str = "multipart/mixed"):
    return f"""
    FROM: {user_from}
    TO:{user_to}
    SUBJECT:{subject}
    MIME-VERSION: 1.0
    Content-type: {content_type}; boundary={boundary_word}
    """


def make_data(user_from: str, user_to: str, subject: str, text_message: str, files_to_join: list[str],
              boundary_word: str = "BOUNDARY") -> str:
    mail: str = ""
    # ensuring every email have their proper header
    boundary_format: str = f"\n--{boundary_word}"
    mail += __add_header_to_data(user_from, user_to, subject, boundary_word)
    mail += boundary_format

    # add the text to the email
    mail += __add_text_to_data(text_message)
    mail += boundary_format

    # add the joint pieces to the email
    for e in files_to_join:
        if not os.path.isfile(e):
            continue
        mail += __add_file_to_data(__format_joint_file(e))
        mail += boundary_format

    return mail

#endregion