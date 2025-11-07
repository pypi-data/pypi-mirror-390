import os
import re

from dotenv import load_dotenv

class Config:
    load_dotenv()

    COOKIES_FILE_NAME = os.getenv("COOKIES_FILE_NAME", "inatro_cookies.pkl")
    INATRO_PROTECTED_URL = os.getenv("INATRO_PROTECTED_URL")
    INATRO_LOGIN_URL = os.getenv("INATRO_LOGIN_URL")
    INATRO_LOGIN_POST = os.getenv("INATRO_LOGIN_POST")
    ESTADO_CARTA_URL = os.getenv("ESTADO_CARTA_URL")

    REQUEST_TIMEOUT = 10  # seconds
    DATE_FORMAT = "%Y-%m-%d"
    CARD_PATTERN = re.compile(r"^\d+$")
    

    # Centralized error codes for login-related failures to keep messages consistent.
    error_codes = {
        "missing_fields": {
            "code": "LOGIN_001",
            "message": "Both driver license number and birth date are required."
        },
        "invalid_carta_format": {
            "code": "LOGIN_002",
            "message": "Driver license number must contain only digits."
        },
        "invalid_birthdate_format": {
            "code": "LOGIN_003",
            "message": "Birth date must follow the YYYY-MM-DD format."
        },
        "login_failed": {
            "code": "LOGIN_004",
            "message": "Invalid credentials provided; login request was rejected."
        },
        "unexpected_response": {
            "code": "LOGIN_005",
            "message": "Unexpected response received from login endpoint."
        },
        "network_error": {
            "code": "LOGIN_006",
            "message": "Network error occurred while attempting to reach the login endpoint."
        },
        "response_parse_error": {
            "code": "LOGIN_007",
            "message": "Unable to parse response data from login endpoint."
        }
    }
