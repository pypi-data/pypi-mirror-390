import typer
from typing_extensions import Annotated
from dektools.web.url import Url
from ...registry.staticfiles import StaticfilesRegistry

app = typer.Typer(add_completion=False)


@app.command()
def login(
        name,
        registry,
        username: Annotated[str, typer.Argument()] = "",
        password: Annotated[str, typer.Argument()] = ""):
    url = Url.new(registry)
    username = username or url.username
    password = password or url.password
    StaticfilesRegistry(registry).login(name=name, username=username, password=password)


@app.command()
def logoff(registry: str):
    StaticfilesRegistry(registry).logoff()


@app.command()
def push(registry: str, path: str, version: Annotated[str, typer.Argument()] = ""):
    StaticfilesRegistry(registry).push(path, version=version)


@app.command()
def pull(registry: str, path: str, version: Annotated[str, typer.Argument()] = ""):
    StaticfilesRegistry(registry).pull(path, version=version)
