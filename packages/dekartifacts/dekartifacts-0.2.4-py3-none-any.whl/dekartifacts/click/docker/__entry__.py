import re
import os
import sys
import json
import base64
import typing
import shlex
import typer
from typing import List
from typing_extensions import Annotated
from dektools.web.url import Url
from dektools.file import read_lines, remove_path, write_file
from dektools.typer import command_mixin, multi_options_to_dict, annotation
from dektools.shell import shell_wrapper
from dektools.fetch import download_dir, download_content
from dektools.net import get_local_ip_list
from dektools.str import to_slice
from ...artifacts.docker import DockerArtifact
from .aio import app as aio_app
from .static import app as static_app

app = typer.Typer(add_completion=False)

app.add_typer(aio_app, name='aio')
app.add_typer(static_app, name='static')


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
        DockerArtifact.login(registry, username, password)
    else:
        DockerArtifact.login_all_env()


@app.command()
def auths(
        items: Annotated[List[str], typer.Argument()] = None,
        b64: Annotated[bool, typer.Option("--base64/--no-base64")] = False):
    data_list = []
    for item in items:
        registry, username, password = item.split(':')
        data_list.append(dict(
            registry=registry, username=username, password=password
        ))
    data = DockerArtifact.auths(*data_list)
    if b64:
        result = base64.b64encode(json.dumps(data, indent=4).encode('utf-8')).decode('ascii')
    else:
        result = json.dumps(data)
    sys.stdout.write(result)


@app.command()
def filename(images: Annotated[List[str], typer.Argument()] = None):
    print(' '.join(DockerArtifact.url_to_filename(image) for image in images), end='', flush=True)


def _split_images(images):
    return [x for x in re.split(r'[,;\r\n ]', images) if x]


def _get_images(images):
    if images:
        return _split_images(images)
    else:
        return DockerArtifact.images()


@app.command()
def rm_none(image: Annotated[str, typer.Argument()] = None):
    DockerArtifact.clean_none_images(image)


@app.command()
def rm(images: Annotated[List[str], typer.Argument()] = None):
    for image in images:
        DockerArtifact.remove(image)


@app.command()
def rm_tags(image, item: Annotated[str, typer.Argument()] = None, safe: bool = False):
    tags = DockerArtifact.tags(image)
    if item:
        tags = tags[to_slice(item)]
    for tag in tags:
        DockerArtifact.remove(f"{image}:{tag}", safe=safe)


@app.command()
def remove(image, safe: bool = False, last: bool = False, dry_run: bool = False):
    items = DockerArtifact.pick(image)
    if last:
        items = items[:-1]
    for item in items:
        if dry_run:
            print(f"Removing {item}")
        else:
            DockerArtifact.remove(item, safe=safe)


@app.command()
def latest(
        image,
        full: Annotated[bool, typer.Option("--full/--no-full")] = True,
        local: Annotated[bool, typer.Option("--local/--no-local")] = True,
        number: Annotated[bool, typer.Option("--number/--no-number")] = True,
        prefix: str = ""
):
    result = DockerArtifact.get_latest_tag(image, local, number, prefix)
    if result:
        print(f"{image}:{result}" if full else result, end='', flush=True)


@app.command()
def exports(path, images: Annotated[List[str], typer.Argument()] = None):
    images = images or DockerArtifact.images()
    DockerArtifact.exports(images, path)


@app.command()
def imports(path, skip=True):
    DockerArtifact.imports(path, skip)


_serve_fetch_port = 8880


@app.command()
def serve(
        path, images: Annotated[List[str], typer.Argument()] = None,
        safe: bool = False, port: int = _serve_fetch_port):
    DockerArtifact.exports(images, path)
    write_file(os.path.join(path, 'index'), s=' '.join(os.listdir(path)))
    cmd = f'{sys.executable} -m http.server -d "{path}"'
    if safe:
        cmd += '-b 0.0.0.0'
    cmd += f" {port}"
    print('Local ip list:')
    print('\n'.join(get_local_ip_list()), flush=True)
    shell_wrapper(cmd)


@app.command()
def fetch(path, server):
    if server == 'localhost' or re.fullmatch('[0-9]+.[0-9]+.[0-9]+.[0-9]+', server):
        server = f"http://{server}:{_serve_fetch_port}"
    server = server.rstrip('/')
    index = download_content(f"{server}/index").decode('utf-8')
    files = [x for x in index.split()]
    download_dir(path, [f"{server}/{file}" for file in files])


@app.command()
def sync(
        path,
        images: Annotated[List[str], typer.Argument()] = None,
        force: Annotated[bool, typer.Option("--force/--no-force")] = True):
    if os.path.exists(path) or force:
        images = images or DockerArtifact.images()
        DockerArtifact.exports(images, path)
        DockerArtifact.imports(path)


@app.command()
def sync_keep(
        path, images: Annotated[List[str], typer.Argument()] = None,
        running: Annotated[bool, typer.Option("--running/--no-running")] = True,
        tag: Annotated[bool, typer.Option("--tag/--no-tag")] = True
):
    def goon():  # if `docker ps` is empty
        return running or not list(DockerArtifact.container_active(True))

    if not goon():
        return
    image_no_tag = {x.split(':')[0] for x in images}
    for image in DockerArtifact.images():
        if tag:
            ok = image not in images
        else:
            ok = image.split(':')[0] not in image_no_tag
        if ok:
            if goon():
                DockerArtifact.remove(image)
                remove_path(os.path.join(path, DockerArtifact.url_to_filename(image)))
    if goon():
        DockerArtifact.remove_none()


@command_mixin(app)
def cp(args, image, ignore: Annotated[bool, annotation.Option("--ignore/--no-ignore")] = False):
    DockerArtifact.cp(image, *shlex.split(args), ignore=ignore)


@app.command()
def migrate(path, items, registry, ga='', la=''):
    DockerArtifact.imports(path, False)
    for image in read_lines(items, skip_empty=True):
        image_new = f"{registry}/{image.split('/', 1)[-1]}"
        DockerArtifact.tag(image, image_new)
        DockerArtifact.push(image_new, ga=ga, la=la)
        DockerArtifact.remove(image)
        DockerArtifact.remove(image_new)


@app.command()
def clean_none(args=''):
    DockerArtifact.clean_none_images(args)


@app.command()
def build(
        path,
        image: typing.Optional[typing.List[str]] = typer.Option(None),
        basic=None, step=None, base=None,
        arg: typing.Optional[typing.List[str]] = typer.Option(None),
        options=None,
        context=None,
        push: Annotated[bool, typer.Option("--push/--no-push")] = True,
        push_only_last: Annotated[bool, typer.Option("--last/--no-last")] = False,
        remove: Annotated[bool, typer.Option("--remove/--no-remove")] = False
):
    images = multi_options_to_dict(image)
    args = multi_options_to_dict(arg)
    DockerArtifact.build_fast(path, images, basic, step, base, args, options, context, push, push_only_last, remove)


@app.command()
def push(image: str, ga="", la=""):
    DockerArtifact.push(image, ga, la)


@app.command()
def pull(image: str, ga="", la=""):
    DockerArtifact.pull(image, ga, la)
