import click
import requests
from pathlib import Path
from urllib.parse import quote

from cli.utils.config import get_api_client
from cli.utils.vault_ignore import should_ignore_var
from cli.utils.api import get_auth_headers


def find_env_files():
    """현재 디렉토리와 하위 디렉토리에서 환경 파일들을 찾습니다."""
    current_dir = Path.cwd()
    env_files = []

    # .env 파일 찾기 (현재 디렉토리만)
    env_file = current_dir / ".env"
    if env_file.exists() and env_file.stat().st_size > 0:
        rel_path = str(env_file.relative_to(Path.cwd()))
        if not should_ignore_var(rel_path):
            env_files.append(env_file)

    # .env.* 파일 찾기 (현재 디렉토리와 하위 디렉토리)
    for file in current_dir.rglob(".env.*"):
        if file.name != ".env.vault.yml" and file.stat().st_size > 0:  # vault 설정 파일 제외 및 빈 파일 제외
            rel_path = str(file.relative_to(Path.cwd()))
            if not should_ignore_var(rel_path):
                env_files.append(file)

    return env_files


@click.command(name="push")
@click.option("--force", "-f", is_flag=True, help="서버의 기존 파일을 모두 삭제하고 현재 파일만 업로드")
def push(force):
    """서버에 환경 파일 업로드

    현재 디렉토리의 환경 파일들을 서버에 업로드합니다.
    --force 옵션을 사용하면 서버의 기존 파일을 모두 삭제하고 현재 파일만 업로드합니다.
    """
    try:
        # 환경 파일 찾기
        env_files = find_env_files()

        if not env_files:
            click.echo("업로드할 환경 파일이 없습니다.")
            return

        # API 클라이언트 설정
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

        # force 옵션이 있는 경우 서버의 기존 파일 목록 조회
        if force:
            response = requests.get(
                f"{server_url}/api/v1/files/{encoded_vault_id}/files",
                headers=headers
            )

            if response.status_code == 200:
                existing_files = response.json()
                if existing_files:
                    click.echo("\n서버에 있는 파일 목록:")
                    for file_path in sorted(existing_files):
                        click.echo(f"🗑️  {file_path}")

                    click.echo("\n로컬에 있는 파일 목록:")
                    for env_file in sorted(env_files):
                        click.echo(f"  - {env_file.relative_to(Path.cwd())}")

                    if not click.confirm("\n서버의 기존 파일을 모두 삭제하고 현재 파일만 업로드하시겠습니까?"):
                        click.echo("작업이 취소되었습니다.")
                        return

                    click.echo("\n기존 파일 삭제 중...")
                    for file_path in existing_files:
                        # 기존 파일 삭제
                        delete_response = requests.delete(
                            f"{server_url}/api/v1/files/{encoded_vault_id}/files/{quote(file_path, safe='')}",
                            headers=headers
                        )
                        if delete_response.status_code == 200:
                            click.echo(f"✓ '{file_path}' 파일이 삭제되었습니다.")
                        else:
                            click.echo(f"✗ '{file_path}' 파일 삭제 실패", err=True)

        # 파일 내용 읽기 및 업로드
        files_content = {}
        for env_file in env_files:
            # 상대 경로 계산
            rel_path = str(env_file.relative_to(Path.cwd()))
            with open(env_file, 'r') as f:
                files_content[rel_path] = f.read()

        # 파일 업로드
        response = requests.post(
            f"{server_url}/api/v1/files/{encoded_vault_id}/files",
            headers=headers,
            json=files_content
        )

        if response.status_code != 200:
            click.echo(
                f"파일 업로드 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        click.echo(f"'{vault_name}' 볼트에 {len(files_content)}개의 파일이 업로드되었습니다.")

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
