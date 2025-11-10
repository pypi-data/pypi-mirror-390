import typer
from typing_extensions import Annotated
from dektools.web.url import Url
from ...registry.docker import DockerRegistry

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
    DockerRegistry(registry).login(nmae=name, username=username, password=password)


@app.command()
def logoff(registry: str):
    DockerRegistry(registry).logoff()


@app.command()
def push(registry: str, image: str):
    DockerRegistry(registry).push(image)


@app.command()
def pull(registry: str, image: str):
    DockerRegistry(registry).pull(image)
