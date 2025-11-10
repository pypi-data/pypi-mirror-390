from dektools.typer import command_version
from . import app
from .registry.__entry__ import app as registry_app
from .docker.__entry__ import app as docker_app
from .helm import app as helm_app
from .staticfiles import app as staticfiles_app

command_version(app, __name__)
app.add_typer(registry_app, name='registry')
app.add_typer(docker_app, name='docker')
app.add_typer(helm_app, name='helm')
app.add_typer(staticfiles_app, name='staticfiles')


def main():
    app()
