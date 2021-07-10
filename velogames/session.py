from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup  # type: ignore


class Session:
    def __init__(self, state):
        self._state = state
        self._session = requests.Session()
        self._cache = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._session.close()
        self.clear()

    @property
    def size(self):
        return len(self._cache)

    def clear(self):
        self._cache = {}

    def fetch(
        self, *parts: str, params: Optional[Dict[str, Any]] = None
    ) -> BeautifulSoup:
        url = self._state["url"]

        for part in parts:
            url = urljoin(url, part)
        if params:
            url += "?" + urlencode({k: v for k, v in params.items() if v is not None})

        if url in self._cache:
            return self._cache[url]

        response = self._session.get(url)
        response.raise_for_status()

        parser = BeautifulSoup(response.text, features="html.parser")
        self._cache[url] = parser

        return parser
