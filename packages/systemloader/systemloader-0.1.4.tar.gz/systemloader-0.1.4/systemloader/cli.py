import click
from systemloader.commands.update import init_engine, update_engine


@click.group()
def main():
    """systemloader"""
    pass


@main.command()
def init():
    init_engine()
    click.echo('Engine OK!')


@main.command()
def update():
    update_engine()
    click.echo('Update system')


if __name__ == '__main__':
    main()
