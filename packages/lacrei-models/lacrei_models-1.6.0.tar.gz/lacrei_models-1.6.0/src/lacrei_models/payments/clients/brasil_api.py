import logging

import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger("celery")


class BrasilAPIClient:
    BASE_URL = "https://brasilapi.com.br/api"

    def __init__(self, version: str = "v1", *args, **kwargs):
        self.version = version

    def get_banks(self):
        url = f"{self.BASE_URL}/banks/{self.version}/"
        try:
            response = requests.get(url, timeout=4)
            response.raise_for_status()
            data = response.json()
            return data if data else []
        except (RequestException, Timeout):
            logger.error("Erro ao buscar dados na API de bancos", exc_info=True)
            return []
