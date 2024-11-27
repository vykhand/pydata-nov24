import logging, sys
import os
import base64
from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(os.environ['LOG_LEVEL'])

    formatter = logging.Formatter('[%(asctime)s] {%(module)s.%(funcName)s:%(lineno)d %(levelname)s} - %(message)s')
    # '%m-%d %H:%M:%S'
    handl = logging.StreamHandler(stream=sys.stdout)
    handl.setFormatter(formatter)
    log.addHandler(handl)
    return log

def text_to_base64(text):
    # Convert text to bytes using UTF-8 encoding
    bytes_data = text.encode('utf-8')

    # Perform Base64 encoding
    base64_encoded = base64.b64encode(bytes_data)

    # Convert the result back to a UTF-8 string representation
    base64_text = base64_encoded.decode('utf-8')

    return base64_text