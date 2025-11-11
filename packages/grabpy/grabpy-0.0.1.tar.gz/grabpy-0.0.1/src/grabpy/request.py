import requests
import sys


class Requester:
    def __init__(self, retries: int):
        """Set retries to -1 to retry indefinitely"""
        self.retries = retries

    def fetch(self, url: str) -> bytes:
        retries: int = self.retries

        while retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                print(err, file=sys.stderr)

                if err.response.status_code == 404:
                    break

                retries -= 1
            else:
                return response.content

        return b''
