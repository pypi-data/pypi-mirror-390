import click
import os
import yaml
from pathlib import Path
from cli.utils.vault_ignore import get_ignored_vars


@click.command()
@click.option("--vault", "-v", help="볼트 이름")
@click.option("--force", "-f", is_flag=True, help="기존 설정 덮어쓰기")
def init(vault, force):
    """프로젝트 초기화

    현재 디렉토리에 .env.vault.yml 설정 파일을 생성하고 프로젝트를 초기화합니다.
    """
    config_file = Path(".env.vault.yml")
    vault_ignore_file = Path(".vaultignore")

    if config_file.exists() and not force:
        click.echo("이미 초기화된 프로젝트입니다. 덮어쓰려면 --force 옵션을 사용하세요.")
        return

    if not vault:
        vault = click.prompt(
            "볼트 이름을 입력하세요", default=os.path.basename(os.getcwd()))

    config = {
        "vault": vault,
        "server": "https://your-server-url",
    }

    with open(config_file, "w") as f:
        yaml.dump(config, f, sort_keys=False, indent=2, allow_unicode=True)

    # .vaultignore 파일 생성 (없는 경우에만)
    if not vault_ignore_file.exists():
        with open(vault_ignore_file, "w") as f:
            f.write("# 무시할 환경 변수 목록\n")
            f.write("# 각 줄에 하나의 환경 변수 이름을 입력하세요\n")
            f.write("# 예시:\n")
            f.write("# LOCAL_API_KEY\n")
            f.write("# DEV_SECRET\n")
        click.echo("새로운 .vaultignore 파일이 생성되었습니다.")

    click.echo(f"프로젝트가 초기화되었습니다. 볼트: {vault}")
    click.echo("다음 명령어로 로그인하세요: uv run deeply-vault login")
