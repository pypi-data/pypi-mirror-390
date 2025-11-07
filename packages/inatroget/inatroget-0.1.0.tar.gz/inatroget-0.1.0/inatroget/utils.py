from typing import Any, Dict, Optional

from inatroget.config import Config

app_config = Config()

def build_error(code_key: str, extra_detail: Optional[str] = None) -> Dict[str, Any]:
    error_info = app_config.error_codes.get(code_key, {})
    code = error_info.get("code", code_key)
    message = error_info.get("message", "Error occurred.")
    if extra_detail:
        message = f"{message} {extra_detail}"
    return {
        "success": False,
        "code": code,
        "message": message
    }
