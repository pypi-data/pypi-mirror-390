from . import app
from .docker import app as docker_app
from .helm import app as helm_app
from .staticfiles import app as staticfiles_app

app.add_typer(docker_app, name='docker')
app.add_typer(helm_app, name='helm')
app.add_typer(staticfiles_app, name='staticfiles')
