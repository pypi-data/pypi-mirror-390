import click
from pathlib import Path
from rich.console import Console
from rich.table import Table


def parse_env_file(file_path: Path):
    """환경 파일을 파싱하여 변수와 값을 반환합니다."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.splitlines()

        variables = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    variables[key.strip()] = value.strip()
                except ValueError:
                    continue

        return variables
    except Exception:
        return {}


@click.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def diff(file1, file2):
    """환경 변수 비교

    두 환경 파일의 차이점을 비교합니다.
    """
    try:
        file1_path = Path(file1)
        file2_path = Path(file2)

        # 파일 파싱
        vars1 = parse_env_file(file1_path)
        vars2 = parse_env_file(file2_path)

        # 차이점 분석
        added = set(vars2.keys()) - set(vars1.keys())
        removed = set(vars1.keys()) - set(vars2.keys())
        common = set(vars1.keys()) & set(vars2.keys())
        modified = {k for k in common if vars1[k] != vars2[k]}

        # 결과 표시
        console = Console()
        table = Table(title=f"파일 비교: {file1_path.name} vs {file2_path.name}")
        table.add_column("변경 유형", style="cyan")
        table.add_column("변수", style="green")
        table.add_column("값", style="yellow")

        # 추가된 변수
        for key in sorted(added):
            table.add_row("추가", key, vars2[key])

        # 삭제된 변수
        for key in sorted(removed):
            table.add_row("삭제", key, vars1[key])

        # 수정된 변수
        for key in sorted(modified):
            table.add_row("수정", key, f"{vars1[key]} → {vars2[key]}")

        if added or removed or modified:
            console.print(table)
        else:
            click.echo("두 파일이 동일합니다.")

    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
