import click
import requests
from pathlib import Path
from urllib.parse import quote

from cli.utils.config import get_api_client
from cli.utils.vault_ignore import should_ignore_var
from cli.utils.api import get_auth_headers


@click.command(name="pull")
def pull():
    """서버에서 환경 파일 다운로드

    서버의 환경 파일들을 현재 디렉토리에 다운로드합니다.
    .vaultignore 파일을 통해 무시할 파일을 지정할 수 있습니다.
    """
    try:
        # API 클라이언트 설정
        api_client = get_api_client()
        server_url, vault_name = api_client["server"], api_client["vault"]

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

        # 파일 다운로드
        response = requests.put(
            f"{server_url}/api/v1/files/{encoded_vault_id}/sync/pull",
            headers=headers
        )

        if response.status_code != 200:
            click.echo(
                f"파일 다운로드 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        # 파일 저장
        files_content = response.json().get('files', {})
        downloaded_count = 0
        ignored_count = 0
        ignored_files = []

        for file_path, content in files_content.items():
            # .vaultignore에 지정된 파일은 무시
            if should_ignore_var(file_path):
                ignored_count += 1
                ignored_files.append(file_path)
                continue

            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                # 딕셔너리인 경우 content 필드의 값만 추출
                if isinstance(content, dict):
                    content = content.get('content', '')
                f.write(content)
            click.echo(f"✓ '{file_path}' 파일이 다운로드되었습니다.")
            downloaded_count += 1

        click.echo('')
        click.echo(
            f"'{vault_name}' 볼트에서 {downloaded_count}개의 파일이 다운로드되었습니다.")
        
        # 무시된 파일이 있을 경우 메시지 출력
        if ignored_count > 0:
            click.echo(f"\n{ignored_count}개의 파일이 .vaultignore에 의해 무시되었습니다:")
            for ignored_file in sorted(ignored_files):
                click.echo(click.style(f"  - {ignored_file}", fg="yellow"))

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
