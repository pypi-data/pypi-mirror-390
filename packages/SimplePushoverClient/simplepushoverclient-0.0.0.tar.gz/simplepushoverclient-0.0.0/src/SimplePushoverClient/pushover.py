import requests

from simplepushoverclient.models import SendMessageModel
from simplepushoverclient.exceptions import PushoverExceptionResponse

PUSHOVER_API_URL: str = r"https://api.pushover.net/1/messages.json"


class PushoverClient:
    """A client for sending Pushover messages"""

    token: str

    def __init__(self, token: str):
        """initializes the Pushover client

        Args:
            token (str): Pushover API Token
        """
        self.token = token

    def send(self, user: str, message: str, device: str = None, title: str = None) -> int:
        """Sends a message via Pushover to the user.

        Args:
            user (str): user key to send message to
            message (str): message content
            device (str, optional): device to message. Defaults to None.
            title (str, optional): title of the message. Defaults to None.

        Returns:
            int: HTTP status code
        """
        model = SendMessageModel(token=self.token, user=user, message=message, device=device, title=title)

        r = requests.post(PUSHOVER_API_URL, json=model.dump())

        if r.status_code != 200:
            error: str = ""
            resp_json: dict = r.json()

            # parse error message from response
            if "errors" in resp_json:
                if len(resp_json["errors"]) > 0:
                    error = resp_json["errors"][0]

            raise PushoverExceptionResponse(status_code=r.status_code, message=error)
        return r.status_code
