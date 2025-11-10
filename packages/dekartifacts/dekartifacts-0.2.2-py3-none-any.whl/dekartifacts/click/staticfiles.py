import typer
from typing_extensions import Annotated
from dektools.web.url import Url
from ..artifacts.staticfiles import StaticfilesArtifact, get_artifact_staticfiles_by_url

app = typer.Typer(add_completion=False)


@app.command()
def login(
        registry: Annotated[str, typer.Argument()] = "",
        username: Annotated[str, typer.Argument()] = "",
        password: Annotated[str, typer.Argument()] = "",
):
    if registry:
        url = Url.new(registry)
        username = username or url.username
        password = password or url.password
        get_artifact_staticfiles_by_url(registry).login(registry, username, password)
    else:
        StaticfilesArtifact.login_all_env()
