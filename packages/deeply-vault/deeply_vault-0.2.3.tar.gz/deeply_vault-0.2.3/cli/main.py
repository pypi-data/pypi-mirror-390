#!/usr/bin/env python
import click

from cli.commands.init import init
from cli.commands.login import login
from cli.commands.logout import logout
from cli.commands.vault_cmd import vault
from cli.commands.list_cmd import list_cmd
from cli.commands.push import push
from cli.commands.pull import pull
from cli.commands.sync import sync
from cli.commands.status import status
from cli.commands.search import search
from cli.commands.diff import diff
from cli.commands.user import user


@click.group()
@click.version_option(prog_name="deeply-env")
def cli():
    """Deeply CLI - 환경 변수 관리 도구

    dotenv-vault와 유사하게 로컬 .env 파일을 관리하고 서버와 동기화합니다.
    """
    pass


# 명령어 등록
cli.add_command(init)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(vault)
cli.add_command(list_cmd)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(sync)
cli.add_command(status)
cli.add_command(search)
cli.add_command(diff)
cli.add_command(user)


if __name__ == "__main__":
    cli()
