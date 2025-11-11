import click
import requests
from rich.console import Console
from rich.table import Table
from urllib.parse import quote

from cli.utils.config import get_api_client, save_config, get_config
from cli.utils.vault_ignore import get_ignored_vars
from cli.utils.command_utils import CustomMultiCommand
from cli.utils.api import get_auth_headers


@click.group(cls=CustomMultiCommand)
def vault():
    """볼트 관리 명령어"""
    pass


@vault.command()
@click.argument("name")
@click.option("--description", "-d", help="볼트 설명")
@click.option("--kms-key-id", help="AWS KMS 키 ID")
def create(name, description, kms_key_id):
    """새로운 볼트 생성"""
    try:
        api_client = get_api_client()
        server_url = api_client["server"]

        headers = get_auth_headers()

        # KMS 키 ID 입력
        if not kms_key_id:
            kms_key_id = click.prompt("AWS KMS 키 ID를 입력하세요", type=str)

        # 설명 입력
        if not description:
            description = click.prompt("볼트 설명을 입력하세요", type=str, default="")

        response = requests.post(
            f"{server_url}/api/v1/vaults",
            headers=headers,
            json={
                "name": name,
                "kms_key_id": kms_key_id,
                "description": description
            }
        )

        if response.status_code == 200:
            click.echo(f"볼트 '{name}'가 생성되었습니다.")
            
            # .vaultignore 파일이 없으면 생성
            ignored_vars = get_ignored_vars()
            if not ignored_vars:
                with open('.vaultignore', 'w') as f:
                    f.write("# 무시할 환경 변수 목록\n")
                    f.write("# 각 줄에 하나의 환경 변수 이름을 입력하세요\n")
                    f.write("# 예시:\n")
                    f.write("# LOCAL_API_KEY\n")
                    f.write("# DEV_SECRET\n")
                click.echo("새로운 .vaultignore 파일이 생성되었습니다.")
        else:
            click.echo(
                f"볼트 생성 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@vault.command()
@click.argument("name")
def select(name):
    """사용할 볼트 선택"""
    try:
        api_client = get_api_client()
        server_url = api_client["server"]

        headers = get_auth_headers()

        response = requests.get(
            f"{server_url}/api/v1/vaults",
            headers=headers
        )

        if response.status_code != 200:
            click.echo(
                f"볼트 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        vaults = response.json().get('items', [])
        vault_id = None

        for v in vaults:
            if v.get('name') == name:
                vault_id = v.get('id')
                break

        if not vault_id:
            click.echo(f"볼트 '{name}'를 찾을 수 없습니다.", err=True)
            return

        # 설정 저장 (token 제외)
        config = get_config()
        config["vault"] = name
        save_config(config)

        click.echo(f"볼트 '{name}'가 선택되었습니다.")
        
        # .vaultignore 파일 상태 표시
        ignored_vars = get_ignored_vars()
        if ignored_vars:
            click.echo(f"\n현재 {len(ignored_vars)}개의 환경 변수가 .vaultignore에 의해 무시됩니다:")
            for var in sorted(ignored_vars):
                click.echo(click.style(f"  - {var}", fg="yellow"))

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@vault.command(['delete', 'remove'])
@click.argument("name")
def delete(name):
    """볼트 삭제"""
    try:
        api_client = get_api_client()
        server_url = api_client["server"]

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

        vaults = response.json().get('items', [])
        vault_id = None

        for v in vaults:
            if v.get('name') == name:
                vault_id = v.get('id')
                break

        if not vault_id:
            click.echo(f"볼트 '{name}'를 찾을 수 없습니다.", err=True)
            return

        # 삭제 확인
        if not click.confirm(f"정말로 볼트 '{name}'를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."):
            click.echo("삭제가 취소되었습니다.")
            return

        # 볼트 삭제
        encoded_vault_id = quote(vault_id, safe='')
        response = requests.delete(
            f"{server_url}/api/v1/vaults/{encoded_vault_id}",
            headers=headers
        )

        if response.status_code == 204:
            click.echo(f"볼트 '{name}'가 삭제되었습니다.")

            # 현재 선택된 볼트가 삭제된 볼트라면 선택 해제
            config = get_config()
            if config.get("vault") == name:
                config["vault"] = None
                save_config(config)
                click.echo("현재 선택된 볼트가 삭제되어 선택이 해제되었습니다.")
        else:
            click.echo(
                f"볼트 삭제 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@vault.command()
@click.option("--detail", "-d", is_flag=True, help="상세 정보 표시")
def list(detail):
    """볼트 목록 조회"""
    try:
        api_client = get_api_client()
        server_url = api_client["server"]
        current_vault = api_client.get("vault")

        headers = get_auth_headers()

        response = requests.get(
            f"{server_url}/api/v1/vaults",
            headers=headers
        )

        if response.status_code != 200:
            click.echo(
                f"볼트 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        vaults = response.json().get('items', [])
        if not vaults:
            click.echo("볼트가 없습니다.")
            return

        console = Console()
        table = Table(title="볼트 목록")
        table.add_column("이름", style="cyan")
        table.add_column("상태", style="green")
        table.add_column("설명", style="yellow")
        if detail:
            table.add_column("파일 수", style="cyan")

        for vault in vaults:
            name = vault.get('name', '')
            status = "선택됨" if name == current_vault else ""
            description = vault.get('description', '')
            if detail:
                file_count = len(vault.get('files', {}))
                table.add_row(name, status, description, str(file_count))
            else:
                table.add_row(name, status, description)

        console.print(table)

        # .vaultignore 상태 표시
        ignored_vars = get_ignored_vars()
        if ignored_vars:
            click.echo(f"\n현재 {len(ignored_vars)}개의 환경 변수가 .vaultignore에 의해 무시됩니다:")
            for var in sorted(ignored_vars):
                click.echo(click.style(f"  - {var}", fg="yellow"))

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
