import click
import requests
from rich.console import Console
from rich.table import Table

from cli.utils.config import get_api_client
from cli.utils.token import get_token


@click.command()
def status():
    """서버 상태 확인

    서버 연결 상태, 버전 정보, 로그인 상태, 현재 선택된 볼트 정보를 표시합니다.
    """
    try:
        console = Console()
        table = Table(title="Deeply Vault 상태")
        table.add_column("항목", style="cyan")
        table.add_column("상태", style="green")

        # API 클라이언트 설정
        try:
            api_client = get_api_client()
            server_url = api_client["server"]
            vault_name = api_client["vault"]
            token = get_token()

            # 서버 상태 확인
            response = requests.get(f"{server_url}/api/health_check")

            print(response.json())

            if response.status_code == 200:
                server_status = "연결됨"
                version = response.json().get("version", "알 수 없음")
            else:
                server_status = "연결 실패"
                version = "알 수 없음"

            # 로그인 상태
            login_status = "로그인됨" if token else "로그아웃됨"

            # 정보 표시
            table.add_row("서버 상태", server_status)
            table.add_row("서버 버전", version)
            table.add_row("로그인 상태", login_status)
            table.add_row("현재 볼트", vault_name)

        except Exception:
            table.add_row("서버 상태", "연결 실패")
            table.add_row("서버 버전", "알 수 없음")
            table.add_row("로그인 상태", "로그아웃됨")
            table.add_row("현재 볼트", "선택되지 않음")

        console.print(table)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
