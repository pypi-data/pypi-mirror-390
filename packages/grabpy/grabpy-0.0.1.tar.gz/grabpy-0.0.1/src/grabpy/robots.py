from urllib.robotparser import RobotFileParser
import urllib.parse
import time
from functools import lru_cache
import sys


class RobotsParser:
    def __init__(self, useragent: str) -> None:
        self.useragent: str = useragent

    def __str__(self) -> str:
        return f'RobotsParser-{self.useragent}'

    @staticmethod
    def _extract_url_base(url: str) -> str:
        result = urllib.parse.urlparse(url)
        netloc = result.netloc
        scheme = result.scheme

        if not all([netloc, scheme]):
            raise ValueError(f'Invalid url schema: {url}')

        return f'{scheme}://{netloc}'

    @lru_cache(maxsize=128, typed=True)
    def _get_parser(self, url: str) -> RobotFileParser:
        base = self._extract_url_base(url)
        url = urllib.parse.urljoin(base, 'robots.txt')

        rp = RobotFileParser()
        rp.set_url(url)
        rp.read()

        return rp

    def _can_scrape(self, parser: RobotFileParser, url: str) -> bool:
        return parser.can_fetch(self.useragent, url)

    def _scrape_delay(self, parser: RobotFileParser) -> None:
        delay = parser.crawl_delay(self.useragent)

        if not delay:
            return

        time.sleep(float(delay))

    def be_respectful(self, url: str) -> bool:
        try:
            parser = self._get_parser(url)
        except ValueError as err:
            print(err, file=sys.stderr)
            return False

        if not self._can_scrape(parser, url):
            return False

        self._scrape_delay(parser)

        return True
