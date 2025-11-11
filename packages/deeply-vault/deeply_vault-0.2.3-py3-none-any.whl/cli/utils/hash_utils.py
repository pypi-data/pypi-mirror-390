import hashlib


def calculate_hash(content: str) -> str:
    """파일 내용의 해시값을 계산합니다."""
    return hashlib.md5(content.encode()).hexdigest()
