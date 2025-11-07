import pickle
from pathlib import Path
from typing import Optional

import requests
from requests.exceptions import RequestException

from inatroget.config import Config

app_config = Config()
COOKIE_PATH = Path(app_config.COOKIES_FILE_NAME)


def save_cookies(session: requests.Session, destination: Optional[Path] = None) -> Path:
    """Persist the session cookies to disk."""
    cookie_path = Path(destination) if destination else COOKIE_PATH
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    with cookie_path.open("wb") as cookie_file:
        pickle.dump(session.cookies, cookie_file)
    return cookie_path


def is_session_valid(session: requests.Session, timeout: int = 10) -> bool:
    """Verifica se a sessão está válida tentando acessar uma página protegida."""
    protected_url = app_config.INATRO_PROTECTED_URL
    try:
        response = session.get(protected_url, timeout=timeout)
    except RequestException:
        return False
    return response.status_code == 200
