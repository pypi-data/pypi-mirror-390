import typer
from ...artifacts.docker import DockerArtifact

app = typer.Typer(add_completion=False)


@app.command()
def push(filepath: str, image: str):
    DockerArtifact.static_build(filepath, image)


@app.command()
def pull(image: str, filepath: str):
    DockerArtifact.static_fetch_at(image, filepath)
