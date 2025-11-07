import os

from requests import HTTPError
from urllib3.exceptions import ProtocolError

MAX_RESPONSE_LENGTH = os.getenv('NETDOT_CLI_EXCEPTIONS_MAX_LENGTH', None)


class NetdotError(Exception):
    pass


class NetdotLoginError(NetdotError):
    pass


class NetdotRESTError(NetdotError):
    def __init__(self, message, status_code=None, response=None, max_response_length=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        combined_message = message
        if status_code:
            combined_message += f"\nHTTP Status: {status_code}"
        if response:
            if max_response_length and len(str(response)) > max_response_length:
                response_str = str(response)[:max_response_length] + '...trimmed for brevity...' 
            else: 
                response_str = str(response)
            combined_message += f"""\nHTTP Response (below):

{response_str}
"""
        super().__init__(combined_message)


class NetdotDeleteError(NetdotRESTError):
    pass


__all__ = [
    'NetdotError',
    'NetdotLoginError',
    'HTTPError',
    'ProtocolError',
    'NetdotRESTError',
    'NetdotDeleteError',
]
