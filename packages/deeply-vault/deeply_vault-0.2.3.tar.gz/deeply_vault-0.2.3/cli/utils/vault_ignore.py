import os
import fnmatch
from typing import List, Set
from pathlib import Path


def get_ignored_vars() -> tuple[set[str], set[str]]:
    """
    .vaultignore 파일에서 무시할 환경 변수 패턴 목록을 읽어옵니다.
    .gitignore와 유사한 문법을 지원합니다:
    - *: 모든 문자와 매칭
    - ?: 단일 문자와 매칭
    - **: 모든 하위 디렉토리와 매칭
    - !: 예외 패턴
    파일이 없거나 읽기 오류가 발생하면 빈 집합을 반환합니다.
    Returns a tuple of (ignore_patterns, negate_patterns)
    """
    ignore_patterns = []
    negate_patterns = []
    
    # 현재 디렉토리에서 .vaultignore 파일 찾기
    vault_ignore_path = Path('.vaultignore')
    
    if not vault_ignore_path.exists():
        return set(), set()
    
    try:
        with open(vault_ignore_path, 'r') as f:
            for line in f:
                # 주석과 빈 줄 무시
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('!'):
                        # 예외 패턴
                        negate_patterns.append(line[1:])
                    else:
                        # 일반 패턴
                        ignore_patterns.append(line)
    except Exception:
        return set(), set()
    
    return set(ignore_patterns), set(negate_patterns)


def should_ignore_var(var_name: str) -> bool:
    """
    주어진 환경 변수가 .vaultignore 패턴과 매칭되는지 확인합니다.
    파일이 없거나 읽기 오류가 발생하면 False를 반환합니다.
    """
    try:
        ignore_patterns, negate_patterns = get_ignored_vars()
        
        # 예외 패턴이 먼저 매칭되면 무시하지 않음
        for pattern in negate_patterns:
            if fnmatch.fnmatch(var_name, pattern):
                return False
        
        # 무시 패턴 매칭
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(var_name, pattern):
                return True
        
        return False
    except Exception:
        return False


def filter_env_vars(env_vars: dict) -> dict:
    """
    .vaultignore 패턴과 매칭되는 환경 변수를 필터링합니다.
    파일이 없거나 읽기 오류가 발생하면 모든 환경 변수를 반환합니다.
    """
    try:
        return {k: v for k, v in env_vars.items() if not should_ignore_var(k)}
    except Exception:
        return env_vars 