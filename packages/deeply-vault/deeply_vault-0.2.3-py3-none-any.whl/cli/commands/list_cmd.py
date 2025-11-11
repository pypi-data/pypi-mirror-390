from urllib.parse import quote
import click
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table

from cli.utils.config import get_api_client
from cli.utils.vault_ignore import get_ignored_vars, should_ignore_var
from cli.utils.api import get_auth_headers


def find_env_files():
    """현재 디렉토리와 하위 디렉토리에서 환경 파일들을 찾습니다."""
    current_dir = Path.cwd()
    env_files = []

    # .env 파일 찾기 (현재 디렉토리만)
    env_file = current_dir / ".env"
    if env_file.exists():
        env_files.append(env_file)

    # .env.* 파일 찾기 (현재 디렉토리와 하위 디렉토리)
    for file in current_dir.rglob(".env.*"):
        if file.name != ".env.vault.yml":  # vault 설정 파일 제외
            env_files.append(file)

    return env_files


@click.command(name="list")
@click.option("--remote", "-r", is_flag=True, help="서버의 파일 목록 조회")
@click.option("--local", "-l", is_flag=True, help="로컬 환경 파일 목록 조회")
def list_cmd(remote, local):
    """파일 목록 조회

    로컬 환경 파일 또는 서버의 파일 목록을 조회합니다.
    """
    console = Console()

    # 기본적으로 로컬 파일 목록 표시
    if not remote and not local:
        local = True

    try:
        # 로컬 환경 파일 목록 조회
        if local:
            env_files = find_env_files()
            ignore_patterns, negate_patterns = get_ignored_vars()
            
            # 무시되지 않는 파일만 필터링
            filtered_files = []
            ignored_files = []
            
            for file in env_files:
                rel_path = str(file.relative_to(Path.cwd()))
                if should_ignore_var(rel_path):
                    ignored_files.append(file)
                else:
                    filtered_files.append(file)

            table = Table(title="로컬 환경 파일")
            table.add_column("파일 경로", style="cyan")
            table.add_column("크기", style="blue")

            for env_file in sorted(filtered_files, key=lambda x: str(x)):
                # 상대 경로 계산
                rel_path = str(env_file.relative_to(Path.cwd()))

                # 파일 크기
                size = env_file.stat().st_size
                size_str = f"{size} Bytes"

                table.add_row(rel_path, size_str)

            console.print(table)
            
            # 무시된 파일이 있을 경우 메시지 출력
            if ignored_files:
                console.print(f"\n현재 {len(ignored_files)}개의 환경 파일이 .vaultignore에 의해 무시됩니다:")
                for ignored_file in sorted(ignored_files, key=lambda x: str(x)):
                    rel_path = str(ignored_file.relative_to(Path.cwd()))
                    console.print(click.style(f"  - {rel_path}", fg="yellow"))

        # 서버 파일 목록 조회
        if remote:
            api_client = get_api_client()
            server_url = api_client["server"]
            vault_name = api_client["vault"]

            headers = get_auth_headers()

            # 볼트 ID 조회
            response = requests.get(
                f"{server_url}/api/v1/vaults",
                headers=headers
            )

            if response.status_code != 200:
                click.echo(
                    f"볼트 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
                return

            # 볼트 ID 찾기
            vaults = response.json().get('items', [])
            vault_id = None

            for v in vaults:
                if v.get('name') == vault_name:
                    vault_id = v.get('id')
                    break

            if not vault_id:
                click.echo(f"볼트 '{vault_name}'를 찾을 수 없습니다.", err=True)
                return

            encoded_vault_id = quote(vault_id, safe='')

            # 파일 목록 조회
            response = requests.get(
                f"{server_url}/api/v1/files/{encoded_vault_id}/files",
                headers=headers
            )

            if response.status_code != 200:
                click.echo(
                    f"파일 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
                return

            files = response.json()

            if not files:
                click.echo(f"'{vault_name}' 볼트에 파일이 없습니다.")
                return

            table = Table(title=f"서버 파일 목록 ({vault_name})")
            table.add_column("파일 경로", style="cyan")

            for file_path in sorted(files):
                table.add_row(file_path)

            console.print(table)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
