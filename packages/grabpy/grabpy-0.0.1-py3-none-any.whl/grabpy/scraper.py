from .request import Requester
from .robots import RobotsParser
from functools import lru_cache


class Grabber:
    def __init__(self, useragent: str, retries: int = 3) -> None:
        self.robots_parser = RobotsParser(useragent)
        self.requester = Requester(retries)

    def __enter__(self) -> 'Grabber':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return

    @lru_cache(maxsize=8, typed=True)
    def get(self, url: str) -> bytes:
        if not self.robots_parser.be_respectful(url):
            return b''

        return self.requester.fetch(url)
