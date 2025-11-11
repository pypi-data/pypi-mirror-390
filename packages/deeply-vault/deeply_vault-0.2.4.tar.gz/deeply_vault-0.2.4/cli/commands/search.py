import click
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table


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


def search_in_file(file_path: Path, pattern: str, use_regex: bool = False):
    """파일에서 패턴을 검색합니다."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.splitlines()

        matches = []
        for i, line in enumerate(lines, 1):
            if use_regex:
                if re.search(pattern, line):
                    matches.append((i, line))
            else:
                if pattern.lower() in line.lower():
                    matches.append((i, line))

        return matches
    except Exception:
        return []


@click.command()
@click.argument("pattern", required=False)
@click.option("--regex", "-r", is_flag=True, help="정규식 사용")
@click.option("--files-only", "-f", is_flag=True, help="파일명에서만 검색")
@click.option("--content-only", "-c", is_flag=True, help="내용에서만 검색")
def search(pattern, regex, files_only, content_only):
    """환경 변수 검색

    환경 파일에서 키워드를 검색합니다.
    """
    try:
        if not pattern:
            pattern = click.prompt("검색할 키워드를 입력하세요")

        env_files = find_env_files()
        if not env_files:
            click.echo("검색할 환경 파일을 찾을 수 없습니다.")
            return

        console = Console()
        table = Table(title="검색 결과")
        table.add_column("파일", style="cyan")
        table.add_column("라인", style="green")
        table.add_column("내용", style="yellow")

        found = False

        for file_path in env_files:
            rel_path = str(file_path.relative_to(Path.cwd()))

            # 파일명 검색
            if not content_only:
                if regex:
                    if re.search(pattern, file_path.name):
                        table.add_row(rel_path, "-", "파일명 일치")
                        found = True
                else:
                    if pattern.lower() in file_path.name.lower():
                        table.add_row(rel_path, "-", "파일명 일치")
                        found = True

            # 내용 검색
            if not files_only:
                matches = search_in_file(file_path, pattern, regex)
                for line_num, line in matches:
                    table.add_row(rel_path, str(line_num), line)
                    found = True

        if found:
            console.print(table)
        else:
            click.echo(f"'{pattern}'에 대한 검색 결과가 없습니다.")

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
