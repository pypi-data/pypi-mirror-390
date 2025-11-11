import click

from cli.utils.token import delete_token


@click.command()
def logout():
    """서버에서 로그아웃

    저장된 API 토큰을 삭제합니다.
    """
    try:
        if delete_token():
            click.echo("로그아웃되었습니다.")
        else:
            click.echo("이미 로그아웃되어 있습니다.")
    except Exception as e:
        click.echo(f"오류가 발생했습니다: {str(e)}", err=True)
