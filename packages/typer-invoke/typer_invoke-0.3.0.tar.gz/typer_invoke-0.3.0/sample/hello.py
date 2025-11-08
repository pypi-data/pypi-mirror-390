from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def world():
    print('hello world')


@app.command()
def mom():
    print('hello mom')


@app.command(name='other')
def different_name(name: Annotated[str, typer.Argument()]):
    print(f'hello {name}')


if __name__ == '__main__':
    app()
