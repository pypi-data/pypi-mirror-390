import yaml
from pathlib import Path
import click
import os

from cli.utils.token import get_token


def find_config_file():
    """설정 파일 찾기"""
    # 명령어가 실행된 실제 디렉토리
    current_dir = Path(os.getcwd())
    config_file = current_dir / ".env.vault.yml"
    if config_file.exists():
        return config_file

    return None


def get_config_path():
    """설정 파일의 경로를 반환합니다."""
    # 명령어가 실행된 실제 디렉토리
    return Path(os.getcwd()) / ".env.vault.yml"


def get_config():
    """설정 파일을 읽어옵니다."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f) or {}
                return config
            except yaml.YAMLError as e:
                click.echo(f"설정 파일 읽기 오류: {e}", err=True)
                return {}
    else:
        # 디버깅 정보 출력 (필요하면 주석 해제)
        # click.echo(f"설정 파일을 찾을 수 없습니다: {config_path}", err=True)
        # click.echo(f"현재 작업 디렉토리: {os.getcwd()}", err=True)
        return {}


def save_config(config):
    """설정 파일을 저장합니다."""
    # token은 저장하지 않음
    config_to_save = {k: v for k, v in config.items() if k != "token"}
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        yaml.dump(config_to_save, f)


def get_api_client():
    """API 클라이언트 설정을 반환합니다."""
    config = get_config()
    token = get_token()

    if not config:
        raise click.ClickException(
            f"설정 파일({get_config_path()})을 찾을 수 없습니다. 'uv run deeply-vault login -s <서버 URL>' 명령어로 로그인해주세요.")

    if not config.get("server"):
        raise click.ClickException(
            "서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login -s <서버 URL>' 명령어로 로그인해주세요.")

    if not token:
        raise click.ClickException(
            "로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.")

    if not config.get("vault"):
        raise click.ClickException(
            "볼트가 선택되지 않았습니다. 'uv run deeply-vault vault select <볼트 이름>' 명령어로 볼트를 선택해주세요.")

    return {
        "server": config["server"],
        "token": token,
        "vault": config["vault"]
    }


def find_env_files(env_name=None):
    """환경 파일 찾기"""
    if env_name:
        pattern = f".env.{env_name}"
        return list(Path(".").glob(f"**/{pattern}"))
    else:
        # 모든 .env 파일 찾기
        return list(Path(".").glob("**/.env*"))
