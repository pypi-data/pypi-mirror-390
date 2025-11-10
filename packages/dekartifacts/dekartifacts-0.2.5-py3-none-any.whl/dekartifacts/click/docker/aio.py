import typer
from typing import List
from typing_extensions import Annotated
from ...allinone.docker import DockerAllInOne

app = typer.Typer(add_completion=False)


@app.command()
def login():
    DockerAllInOne.login_all_env()


@app.command()
def push(registry: str, images: Annotated[List[str], typer.Argument()] = None):
    DockerAllInOne(registry).push(images)


@app.command()
def pull(registry: str, images: Annotated[List[str], typer.Argument()] = None):
    DockerAllInOne(registry).pull(images)
