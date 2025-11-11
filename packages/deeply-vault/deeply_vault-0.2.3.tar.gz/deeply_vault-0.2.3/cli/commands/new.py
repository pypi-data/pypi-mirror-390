import click
import requests
import yaml
from urllib.parse import quote

from cli.utils.config import get_config, get_api_client
from cli.utils.api import get_auth_headers


@click.command()
@click.argument("vault_name")
@click.option("--description", "-d", help="볼트 설명")
@click.option("--kms-key-id", help="AWS KMS 키 ID")
def new(vault_name, description, kms_key_id):
    """새 볼트 생성 또는 기존 볼트 덮어쓰기

    새로운 환경 변수 볼트를 생성하거나 기존 볼트를 덮어씁니다.
    """
    try:
        api_client = get_api_client()
        server_url = api_client["server"]

        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"

        # KMS 키 ID 입력
        if not kms_key_id:
            kms_key_id = click.prompt("AWS KMS 키 ID를 입력하세요", type=str)

        # 기존 볼트 확인
        response = requests.get(
            f"{server_url}/api/v1/vaults",
            headers=headers
        )

        if response.status_code != 200:
            click.echo(
                f"볼트 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        # 볼트 목록에서 이름으로 검색
        vaults = response.json().get('items', [])

        existing_vault = next(
            (v for v in vaults if v.get('name') == vault_name), None)

        if existing_vault:
            # 기존 볼트가 있으면 덮어쓰기
            vault_id = existing_vault.get('id')
            encoded_vault_id = quote(vault_id, safe='')

            response = requests.patch(
                f"{server_url}/api/v1/vaults/{encoded_vault_id}",
                headers=headers,
                json={
                    "kms_key_id": kms_key_id,
                    "description": description or existing_vault.get('description', '')
                }
            )
            if response.status_code >= 200 and response.status_code < 300:
                click.echo(f"✓ '{vault_name}' 볼트가 업데이트되었습니다.")
            else:
                click.echo(
                    f"✗ 볼트 업데이트 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
                return
        else:
            # 새 볼트 생성
            response = requests.post(
                f"{server_url}/api/v1/vaults",
                headers=headers,
                json={
                    "name": vault_name,
                    "kms_key_id": kms_key_id,
                    "description": description or ""
                }
            )
            if response.status_code >= 200 and response.status_code < 300:
                click.echo(f"✓ '{vault_name}' 볼트가 생성되었습니다.")
            else:
                click.echo(
                    f"✗ 볼트 생성 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
                return

        # 설정 파일 업데이트
        config = get_config()
        config["vault"] = vault_name

        with open(".env.vault.yml", "w") as f:
            yaml.dump(config, f, sort_keys=False, indent=2, allow_unicode=True)

        click.echo(f"현재 프로젝트의 볼트가 '{vault_name}'(으)로 설정되었습니다.")

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
