import click
import requests
from rich.console import Console
from rich.table import Table

from cli.utils.config import get_config
from cli.utils.token import get_token
from cli.utils.api import get_auth_headers

from cli.utils.command_utils import CustomMultiCommand

@click.group(cls=CustomMultiCommand)
def user():
    """사용자 관리 명령어"""
    pass


@user.command()
@click.option('--username', '-u', prompt='사용자 이름', help='생성할 사용자의 이름')
@click.password_option(prompt='비밀번호', confirmation_prompt=True, help='새 사용자의 비밀번호')
def create(username: str, password: str):
    """새 사용자를 생성합니다 (관리자 전용)"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # 사용자 생성 요청
        response = requests.post(
            f"{server_url}/api/v1/auth/register",
            json={"username": username, "password": password},
            headers=get_auth_headers()
        )

        if response.status_code == 201:
            click.echo(f"사용자 '{username}' 생성 완료!")
        elif response.status_code == 403:
            click.echo("이 작업은 관리자만 수행할 수 있습니다.", err=True)
        elif response.status_code == 400:
            click.echo(f"사용자 생성 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
        else:
            click.echo(f"오류 발생: {response.status_code}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@user.command(['delete', 'remove'])
@click.argument('username')
@click.confirmation_option(prompt='정말 이 사용자를 삭제하시겠습니까?')
def delete(username: str):
    """사용자를 삭제합니다 (관리자 전용)"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # 사용자 삭제 요청
        response = requests.delete(
            f"{server_url}/api/v1/auth/users/{username}",
            headers=get_auth_headers()
        )

        if response.status_code == 204:
            click.echo(f"사용자 '{username}' 삭제 완료!")
        elif response.status_code == 403:
            click.echo("이 작업은 관리자만 수행할 수 있습니다.", err=True)
        elif response.status_code == 404:
            click.echo(f"사용자 '{username}'를 찾을 수 없습니다.", err=True)
        else:
            click.echo(f"오류 발생: {response.status_code}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@user.command()
def list():
    """사용자 목록을 조회합니다 (관리자 전용)"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # 사용자 목록 조회 요청
        response = requests.get(
            f"{server_url}/api/v1/auth/users",
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            users = response.json().get("items", [])
            
            # 테이블 생성
            console = Console()
            table = Table(title="사용자 목록")
            
            # 테이블 열 정의
            table.add_column("ID", style="cyan")
            table.add_column("사용자명", style="green")
            table.add_column("API 키", style="yellow")
            table.add_column("마지막 수정", style="blue")
            
            # 데이터 추가
            for user in users:
                user_id = user.get("id", "")
                username = user.get("username", "")
                api_key = "있음" if user.get("api_key") else "없음"
                updated_at = user.get("updated_at", "")
                
                # 타임스탬프를 읽기 쉬운 형식으로 변환
                if updated_at:
                    from datetime import datetime
                    try:
                        dt = datetime.fromtimestamp(updated_at)
                        updated_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                table.add_row(user_id, username, api_key, updated_at)
            
            # 테이블 출력
            console.print(table)
        elif response.status_code == 403:
            click.echo("이 작업은 관리자만 수행할 수 있습니다.", err=True)
        else:
            click.echo(f"사용자 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@user.group(cls=CustomMultiCommand)
def api_key():
    """API 키 관리 명령어"""
    pass


@api_key.command()
def create():
    """새로운 API 키를 생성합니다"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # API 키 생성 요청
        response = requests.post(
            f"{server_url}/api/v1/auth/api-key",
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            api_key = response.json().get("api_key")
            click.echo("API 키 생성 완료!")
            click.echo(f"API 키: {api_key}")
            click.echo("\n⚠️  이 API 키는 이제 다시 표시되지 않으니 안전한 곳에 저장해주세요!")
        else:
            click.echo(f"API 키 생성 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@api_key.command()
def show():
    """현재 사용 중인 API 키를 조회합니다"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # API 키 조회 요청
        response = requests.get(
            f"{server_url}/api/v1/auth/api-key",
            headers=get_auth_headers()
        )

        if response.status_code == 200:
            api_key = response.json().get("api_key")
            click.echo(f"현재 API 키: {api_key}")
        elif response.status_code == 404:
            click.echo("API 키가 생성되지 않았습니다. 'deeply user api-key create' 명령어로 생성해주세요.", err=True)
        else:
            click.echo(f"API 키 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)


@api_key.command(['delete', 'remove'])
@click.confirmation_option(prompt='정말 이 API 키를 삭제하시겠습니까?')
def delete():
    """현재 사용 중인 API 키를 삭제합니다"""
    try:
        config = get_config()
        server_url = config.get("server")
        token = get_token()

        if not server_url:
            click.echo("서버 URL이 설정되지 않았습니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        if not token:
            click.echo("로그인이 필요합니다. 'uv run deeply-vault login' 명령어로 로그인해주세요.", err=True)
            return

        # API 키 삭제 요청
        response = requests.delete(
            f"{server_url}/api/v1/auth/api-key",
            headers=get_auth_headers()
        )

        if response.status_code == 204:
            click.echo("API 키 삭제 완료!")
        elif response.status_code == 404:
            click.echo("API 키가 생성되지 않았습니다.", err=True)
        else:
            click.echo(f"API 키 삭제 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)