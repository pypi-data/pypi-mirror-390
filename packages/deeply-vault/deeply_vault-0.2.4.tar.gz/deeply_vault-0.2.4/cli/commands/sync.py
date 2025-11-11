import click
import requests
import hashlib
from pathlib import Path
from urllib.parse import quote
from rich.console import Console
from rich.syntax import Syntax

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


def get_file_hash(file_path: Path) -> str:
    """파일의 해시값을 계산합니다."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def parse_env_file(content: str) -> dict:
    """환경 변수 파일을 파싱합니다."""
    result = {}
    # content가 딕셔너리인 경우 content 필드의 값만 사용
    if isinstance(content, dict):
        content = content.get('content', '')
    # content가 문자열이 아닌 경우 문자열로 변환
    if not isinstance(content, str):
        content = str(content)
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            try:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
            except ValueError:
                continue
    return result


def show_diff(local_content: str, server_content: str):
    """두 환경 변수 파일의 차이를 git diff 스타일로 보여줍니다."""
    # 서버의 파일 내용이 딕셔너리인 경우 content 필드의 값만 사용
    if isinstance(server_content, dict):
        server_content = server_content.get('content', '')

    local_vars = parse_env_file(local_content)
    server_vars = parse_env_file(server_content)

    # 변경사항 분석
    added = set(local_vars.keys()) - set(server_vars.keys())  # 로컬에만 있는 변수
    removed = set(server_vars.keys()) - set(local_vars.keys())  # 서버에만 있는 변수
    common = set(local_vars.keys()) & set(server_vars.keys())  # 양쪽에 있는 변수
    # 값이 다른 변수
    modified = {k for k in common if local_vars[k] != server_vars[k]}

    if not (added or removed or modified):
        return

    console = Console()
    diff_lines = []

    # 추가된 변수 (로컬에만 있는 변수)
    for key in sorted(added):
        diff_lines.append(f"+ {key}={local_vars[key]}")

    # 삭제된 변수 (서버에만 있는 변수)
    for key in sorted(removed):
        diff_lines.append(f"- {key}={server_vars[key]}")

    # 수정된 변수
    for key in sorted(modified):
        diff_lines.append(f"- {key}={server_vars[key]}")
        diff_lines.append(f"+ {key}={local_vars[key]}")

    diff_content = "\n".join(diff_lines)
    syntax = Syntax(diff_content, "diff", theme="monokai", line_numbers=False)
    console.print(syntax)
    console.print()


@click.command(name="sync")
@click.option("--force", "-f", is_flag=True, help="서버의 파일을 강제로 로컬과 동기화")
def sync(force):
    """서버와 로컬 파일 동기화

    서버의 파일과 로컬 파일을 비교하여 동기화합니다.
    --force 옵션을 사용하면 서버의 파일을 강제로 로컬과 동기화합니다.
    """
    try:
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

        # 서버의 파일 목록 조회
        response = requests.get(
            f"{server_url}/api/v1/files/{encoded_vault_id}/files",
            headers=headers
        )

        if response.status_code != 200:
            click.echo(
                f"서버 파일 목록 조회 실패: {response.json().get('detail', '알 수 없는 오류')}", err=True)
            return

        server_files = response.json()

        # 로컬 파일 목록 조회
        local_files = find_env_files()
        local_files_dict = {str(f.relative_to(Path.cwd()))                            : f for f in local_files}

        # 동기화할 파일 목록 생성
        files_to_upload = []
        files_to_download = []
        files_to_delete = []

        # 서버에만 있는 파일
        for server_file in server_files:
            if server_file not in local_files_dict:
                files_to_download.append(server_file)

        # 로컬에만 있는 파일
        for local_file_path, local_file in local_files_dict.items():
            if local_file_path not in server_files:
                files_to_upload.append(local_file)

        # 양쪽에 있는 파일 (해시 비교)
        for file_path in set(server_files) & set(local_files_dict):
            local_file = local_files_dict[file_path]
            local_hash = get_file_hash(local_file)

            # 서버 파일의 해시 조회
            response = requests.get(
                f"{server_url}/api/v1/files/{encoded_vault_id}/files/{quote(file_path, safe='')}",
                headers=headers
            )

            if response.status_code == 200:
                server_file = response.json()
                server_hash = server_file.get('hash', '')

                if local_hash != server_hash:
                    if force:
                        files_to_upload.append(local_file)
                    else:
                        click.echo(f"\n'{file_path}' 파일이 서버와 다릅니다.")
                        # diff 내용 표시
                        with open(local_file, 'r') as f:
                            local_content = f.read()
                        server_content = server_file.get('content', '')
                        if isinstance(server_content, dict):
                            server_content = server_content.get('content', '')

                        show_diff(local_content, server_content)
                        if click.confirm("서버의 파일로 덮어쓰시겠습니까?"):
                            files_to_download.append(file_path)
                        else:
                            files_to_upload.append(local_file)

        # 동기화 작업 수행
        if files_to_upload or files_to_download or files_to_delete:
            click.echo("\n동기화 작업이 필요합니다:")

            if files_to_upload:
                click.echo(f"\n{click.style('업로드할 파일:', fg='yellow')}")
                for file in sorted(files_to_upload):
                    click.echo(
                        f"  + {click.style(str(file.relative_to(Path.cwd())), fg='yellow')}")

            if files_to_download:
                click.echo(f"\n{click.style('다운로드할 파일:', fg='green')}")
                for file_path in sorted(files_to_download):
                    click.echo(f"  ↓ {click.style(file_path, fg='green')}")

            if not force and not click.confirm("\n동기화를 진행하시겠습니까?"):
                click.echo("동기화가 취소되었습니다.")
                return

            # 파일 업로드
            if files_to_upload:
                click.echo("\n파일 업로드 중...")
                files_content = {}
                for file in files_to_upload:
                    rel_path = str(file.relative_to(Path.cwd()))
                    with open(file, 'r') as f:
                        files_content[rel_path] = f.read()

                # 파일 업로드
                response = requests.post(
                    f"{server_url}/api/v1/files/{encoded_vault_id}/files",
                    headers=headers,
                    json={"files": files_content}  
                )

                if response.status_code == 200:
                    click.echo(f"✓ {len(files_to_upload)}개의 파일이 업로드되었습니다.")
                else:
                    error_detail = response.json().get('detail', '알 수 없는 오류')
                    click.echo(f"✗ 파일 업로드 실패: {error_detail}", err=True)

            # 파일 다운로드
            if files_to_download:
                click.echo("\n파일 다운로드 중...")
                for file_path in files_to_download:
                    response = requests.get(
                        f"{server_url}/api/v1/files/{encoded_vault_id}/files/{quote(file_path, safe='')}",
                        headers=headers
                    )

                    if response.status_code == 200:
                        file_content = response.json().get('content', '')
                        if isinstance(file_content, dict):
                            file_content = file_content.get('content', '')
                        file_path = Path(file_path)
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, 'w') as f:
                            f.write(file_content)
                        click.echo(f"✓ '{file_path}' 파일이 다운로드되었습니다.")
                    else:
                        click.echo(f"✗ '{file_path}' 파일 다운로드 실패", err=True)

            click.echo("\n동기화가 완료되었습니다.")
        else:
            click.echo("모든 파일이 동기화되어 있습니다.")

    except Exception as e:
        print('e ->', e)
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
