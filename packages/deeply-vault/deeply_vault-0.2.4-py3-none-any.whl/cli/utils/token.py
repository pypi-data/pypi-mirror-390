import json
from pathlib import Path


def get_token_path():
    """토큰 파일의 경로를 반환합니다."""
    return Path.home() / ".deeply" / "vault" / "token.json"


def save_token(token: str):
    """토큰을 파일에 저장합니다."""
    token_path = get_token_path()
    token_path.parent.mkdir(parents=True, exist_ok=True)

    with open(token_path, 'w') as f:
        json.dump({"token": token}, f)


def get_token() -> str:
    """저장된 토큰을 반환합니다."""
    token_path = get_token_path()
    if token_path.exists():
        with open(token_path, 'r') as f:
            data = json.load(f)
            return data.get("token", "")
    return ""


def delete_token():
    """저장된 토큰을 삭제합니다."""
    token_path = get_token_path()
    if token_path.exists():
        token_path.unlink()
        return True

    return False
