import typer
from typing import List, Optional
from typing_extensions import Annotated
from dektools.web.url import Url
from dektools.file import iter_dir, write_file
from dektools.serializer.yaml import yaml
from ..artifacts.helm import HelmArtifact, get_artifact_helm_by_url
from ..repo.helm import create_helm_repo

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
        get_artifact_helm_by_url(registry).login(registry, username, password)
    else:
        HelmArtifact.login_all_env()


@app.command()
def build(
        url_base,
        path_out,
        dirs: Annotated[Optional[List[str]], typer.Option('--dir')] = None,
        paths: Annotated[Optional[List[str]], typer.Option('--path')] = None,
):
    repos = []
    for path in dirs:
        for item in iter_dir(path):
            repos.append(write_file(None, c=item))
    for path in paths:
        data = yaml.load(path)
        for key, value in data.items():
            for item in value:
                repos.append(HelmArtifact.url_join(key, *item.split(":")))
    create_helm_repo(url_base, repos, path_out)
