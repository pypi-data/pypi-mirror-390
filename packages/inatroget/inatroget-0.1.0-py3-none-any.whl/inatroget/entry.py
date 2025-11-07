from datetime import datetime
from typing import Any, Dict, Optional

import requests
from requests.exceptions import HTTPError, RequestException

from inatroget.config import Config
from inatroget.cookies import save_cookies
from inatroget.get_info import extract_carta_info, get_carta_info_html
from inatroget.utils import build_error

app_config = Config()

REQUEST_TIMEOUT = app_config.REQUEST_TIMEOUT
DATE_FORMAT = app_config.DATE_FORMAT
CARD_PATTERN = app_config.CARD_PATTERN

LoginResult = Dict[str, Any]


def _validate_login_inputs(n_carta: str, data_nascimento: str) -> Optional[LoginResult]:
    if not n_carta or not data_nascimento:
        return build_error("missing_fields")

    if not CARD_PATTERN.match(n_carta):
        return build_error("invalid_carta_format")

    try:
        datetime.strptime(data_nascimento, DATE_FORMAT)
    except ValueError:
        return build_error("invalid_birthdate_format")

    return None


def _fetch_dashboard(session: requests.Session) -> LoginResult:
    try:
        html_content = get_carta_info_html(session=session, timeout=REQUEST_TIMEOUT)
    except HTTPError as exc:
        status = getattr(exc.response, "status_code", "unknown")
        return build_error(
            "unexpected_response",
            f"Failed to fetch dashboard (status {status})."
        )
    except RequestException as exc:
        return build_error("network_error", str(exc))

    data = extract_carta_info(html_content=html_content)
    return {"success": True, "data": data}


def do_login(n_carta: str, data_nascimento: str) -> LoginResult:
    validation_error = _validate_login_inputs(n_carta, data_nascimento)
    if validation_error:
        return validation_error

    session = requests.Session()

    try:
        response = session.get(app_config.INATRO_LOGIN_URL, timeout=REQUEST_TIMEOUT)
    except RequestException as exc:
        return build_error("network_error", str(exc))

    if response.status_code >= 400:
        return build_error(
            "unexpected_response",
            f"Failed to load login page (status {response.status_code})."
        )

    payload = {
        "n_carta": n_carta,
        "data_nascimento": data_nascimento,
    }

    try:
        login_response = session.post(
            app_config.INATRO_LOGIN_POST,
            data=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except RequestException as exc:
        return build_error("network_error", str(exc))

    if login_response.status_code >= 400:
        return build_error(
            "unexpected_response",
            f"Login request failed (status {login_response.status_code})."
        )

    try:
        response_body = login_response.json()
    except ValueError:
        return build_error("response_parse_error")

    if response_body.get("error"):
        error_detail = response_body.get("message")
        return build_error("login_failed", error_detail)

    result = _fetch_dashboard(session)
    if not result.get("success"):
        return result

    # Persist cookies for future requests; non-critical failures are ignored.
    try:
        save_cookies(session=session)
    except OSError:
        pass

    return result
