import os
import json
import uuid
import time
import base64
import tempfile
import subprocess
from dektools.shell import shell_wrapper, shell_with_input_once, shell_result, shell_exitcode, shell_output
from dektools.file import read_text, write_file, read_lines, sure_dir, remove_path, multi_ext, normal_path, \
    sure_parent_dir
from dektools.dict import assign, list_dedup
from dektools.str import number_tuple
from dektools.serializer.yaml import yaml
from dektools.match import glob_match
from .base import ArtifactBase


class DockerArtifact(ArtifactBase):
    typed = 'docker'
    cli_list = ['docker', 'nerdctl', 'podman']

    image_tag_max_length = 128
    registry_standard = 'docker.io'
    image_file_ext = '.docker.tar'

    @classmethod
    def login(cls, registry='', username='', password=''):
        print(F"Login to {registry}, user: {username[0]}***{username[-1]}")
        ret, _, err = shell_with_input_once(f'{cls.cli} login {registry} -u {username} --password-stdin', password)
        if ret:
            for mark in [b'net/http: TLS handshake timeout']:
                if mark in err:
                    time.sleep(1)
                    print(err, flush=True)
                    cls.login(registry, username, password)
                    break
            else:
                raise subprocess.SubprocessError(err)

    @staticmethod
    def auths(*data_list, encoding='utf-8'):
        auths = {}
        for data in data_list:
            auths[data['registry']] = dict(auth=base64.b64encode(
                f"{data['username']}:{data['password']}".encode(encoding)
            ).decode('ascii'))
        return dict(auths=auths)

    @classmethod
    def pull(cls, image, ga='', la=''):
        image = cls.real_image(image)
        if not cls.exist(image):
            ret, err = shell_result(f'{cls.cli} {ga} pull {la} {image}')
            if ret:
                for mark in ['net/http: TLS handshake timeout']:
                    if mark in err:
                        time.sleep(1)
                        return cls.pull(image)
                else:
                    raise subprocess.SubprocessError(err)
        return image

    @classmethod
    def push(cls, image, ga='', la=''):
        image = cls.real_image(image)
        ret, err = shell_result(f'{cls.cli} {ga} push {la} {image}')
        if ret:
            for mark in ['net/http:', 'dial tcp:']:
                if mark in err:
                    time.sleep(1)
                    print(err, flush=True)
                    cls.push(image)
                    break
            else:
                raise subprocess.SubprocessError(err)

    @classmethod
    def remove(cls, image, args='', safe=True):
        def core():
            try:
                shell_wrapper(f'{cls.cli} {args} rmi -f {image}')
            except subprocess.SubprocessError:
                pass

        image = cls.real_image(image)
        if safe:
            images = cls.images_active(False)
            if image not in images:
                core()
        else:
            core()

    @classmethod
    def remove_none(cls):
        # only for docker
        shell_wrapper(f'{cls.cli} image prune --filter "dangling=true" -f')

    @classmethod
    def tag(cls, image, new_image):
        image = cls.real_image(image)
        new_image = cls.real_image(new_image)
        shell_wrapper(f'{cls.cli} tag {image} {new_image}')

    @classmethod
    def digest(cls, image):
        image = cls.real_image(image)
        result = shell_output(f'{cls.cli} inspect --format "{{{{ index .RepoDigests 0 }}}}" {image}')
        return result.rsplit(':', 1)[-1].strip()

    @classmethod
    def id(cls, name, running=False):
        optional = "" if running else "a"
        return shell_output(f'{cls.cli} ps -{optional}qf "name={name}"').strip() or None

    @classmethod
    def exists(cls, image):
        image = cls.real_image(image)
        return bool(shell_output(f'{cls.cli} images -q {image}').strip())

    @classmethod
    def build(cls, image, path, args=None, dockerfile=None):
        image = cls.real_image(image)
        result = ''
        if dockerfile:
            result += f'-f {dockerfile}'
        if args:
            for k, v in args.items():
                result += f' --build-arg "{k}={v}"'
        print(f'{cls.cli} building...', flush=True)
        shell_wrapper(f'{cls.cli} build -t {image} {result} {path}')
        return image

    @classmethod
    def cp(cls, image, *args, ignore=False):
        image = cls.real_image(image)
        name = f"tmp-cp-{uuid.uuid4().hex}"
        shell_result(f"{cls.cli} create --name {name} {image}")
        for src, dest in zip(args[::2], args[1::2]):
            command = f"{cls.cli} cp {name}:{src} {dest}"
            if ignore:
                shell_result(command)
            else:
                shell_wrapper(command)
        shell_result(f"{cls.cli} rm {name}")

    @classmethod
    def status(cls, id_or_name):
        ret, result = shell_result(f"{cls.cli} inspect {id_or_name}", error=False)
        if ret:
            return None
        return json.loads(result)[0]

    @classmethod
    def clean_none_images(cls, image=None, args=''):
        for iid in cls.get_none_images(image):
            cls.remove(iid, args, False)

    @classmethod
    def get_none_images(cls, image=None):
        args = f'-f reference={image}' if image else '-a'
        images = shell_output(f'{cls.cli} images {args} --format "{{{{ .ID }}}}:{{{{ .Tag }}}}"')
        result = []
        for x in read_lines(None, default=images):
            if ':<none>' in x:
                result.append(x.split(':', 1)[0])
        return result

    @classmethod
    def images(cls, tag=True):
        images = shell_output(
            f'{cls.cli} images -a --format "{{{{ .Repository }}}}::{{{{ .Tag }}}}::{{{{ .CreatedAt }}}}"')
        result = []
        for names in sorted((
                yy for yy in (x.split('::', 2) for x in read_lines(None, default=images))
                if '<none>' not in yy[1]
        ), key=lambda xx: xx[-1]):
            repo, tag, created = names
            if tag:
                result.append(f"{repo}:{tag}")
            else:
                result.append(repo)
        if not tag:
            result = list_dedup(result)
        return result

    @classmethod
    def tags(cls, image, number=True, prefix=None):
        image = cls.real_image(image)
        images = shell_output(
            f'{cls.cli} images -f reference={image} --format '
            f'"{{{{ .Repository }}}}::{{{{ .Tag }}}}::{{{{ .CreatedAt }}}}"')
        return [xx[1] for xx in sorted((
            yy for yy in (x.split('::', 2) for x in read_lines(None, default=images))
            if '<none>' not in yy[1] and yy[0] == image and (not prefix or yy[1].startswith(prefix))
        ), key=lambda xx: number_tuple(xx[1]) if number else xx[-1])]

    @classmethod
    def tag_latest(cls, image, number=True, prefix=None):
        tags = cls.tags(image, number, prefix)
        if tags:
            return tags[-1]

    @classmethod
    def pick(cls, regex):
        items = regex.split(":", 1)
        if len(items) == 1:
            image, tag = items[0], None
        else:
            image, tag = items
        result = []
        for item in cls.images():
            _image, _tag = item.split(":", 1)
            if glob_match(image, _image):
                if not tag or glob_match(tag, _tag):
                    result.append(item)
        return result

    @classmethod
    def images_active(cls, started=False):
        result = []
        for container in cls.container_active(started):
            result.append(shell_output(f'{cls.cli} inspect --format "{{{{ .Image }}}}" {container}').strip())
        return result

    @classmethod
    def container_active(cls, started=False):
        flag = '' if started else '--all'
        containers = shell_output(f'{cls.cli} ps {flag} --format "{{{{ .ID }}}}"')
        return list(read_lines(None, default=containers))

    @classmethod
    def exports(cls, images, path, skip=True):
        sure_dir(path)
        result = {}
        for image in images:
            path_file = os.path.join(path, cls.url_to_filename(image))
            result[image] = path_file
            if not os.path.isfile(path_file) or not skip:
                remove_path(path_file)
                shell_wrapper(f"{cls.cli} save -o {path_file} {image}")
        return result

    @classmethod
    def imports(cls, path, skip=True):
        def load(p):
            fn, ext_list = multi_ext(p, cls.image_file_ext.count('.'))
            if skip and fn in images:
                return
            if ''.join(ext_list) == cls.image_file_ext:
                shell_wrapper(f"{cls.cli} load -i {p}", check=False)

        if skip:
            images = {cls.url_to_docker_tag(x) for x in cls.images()}
        else:
            images = set()

        if os.path.isdir(path):
            for file in os.scandir(path):
                load(os.path.join(path, file.name))
        elif os.path.isfile(path):
            load(path)

    @classmethod
    def exist(cls, image):
        return cls.exists(image)

    @classmethod
    def remote_exists(cls, image):
        image = cls.real_image(image)
        return shell_exitcode(f'skopeo --override-os linux inspect docker://{image}') == 0

    @classmethod
    def remote_exist(cls, image):
        return cls.remote_exists(image)

    @classmethod
    def remote_tags(cls, image, number=True, prefix=None):
        image = cls.real_image(image)
        rc, result = shell_result(f"skopeo --override-os linux list-tags docker://{image}")
        if rc:
            if any(x in result for x in [
                'invalid status code from registry 404',
                'repository name not known to registry',
                "fetching tags list: name unknown",
            ]):
                return []
            elif 'unauthorized' in result:
                return None
            else:
                raise RuntimeError(result)
        data = json.loads(result)['Tags']
        if prefix:
            data = [x for x in data if x.startswith(prefix)]
        if number:
            return sorted(data, key=lambda x: number_tuple(x))
        return data

    @classmethod
    def remote_tag_latest(cls, image, number=True, prefix=None):
        tags = cls.remote_tags(image, number, prefix)
        if tags:
            return tags[-1]

    @classmethod
    def get_latest_tag(cls, image, local=True, number=True, prefix=None):
        if local:
            array = cls.tag_latest, cls.remote_tag_latest
        else:
            array = cls.remote_tag_latest, cls.tag_latest
        for item in array:
            tag = item(image, number, prefix)
            if tag:
                return tag

    @staticmethod
    def format_url(url):
        sha256 = '@sha256'
        repo, tag = url.split(':', 1)
        if repo.endswith(sha256):
            repo = repo[:-len(sha256)]
        return ':'.join([repo.replace('.', '-').replace('/', '-'), tag])

    @classmethod
    def full_url(cls, full_url):
        if ':' not in full_url:
            full_url = f'{full_url}:latest'
        r = full_url.split('/')
        if len(r) <= 1 or '.' not in r[0]:
            return f'{cls.registry_standard}/{full_url}'
        return full_url

    @classmethod
    def is_in_standard(cls, url):
        return cls.full_url(url).startswith(cls.registry_standard)

    @classmethod
    def url_to_docker_tag(cls, url):
        url = cls.full_url(url)
        rr, tag = url.rsplit(':', 1)
        tag_new = rr.split('/', 1)[-1].replace('/', '-') + '-' + tag
        return cls.normalize_docker_tag(url, tag_new)

    @classmethod
    def url_to_filename(cls, url):
        return f"{cls.url_to_docker_tag(url)}{cls.image_file_ext}"

    @classmethod
    def real_image(cls, image):
        sep = cls.url_seps[0]
        index = image.find(sep)
        if index == -1:
            return image
        else:
            registry = image[:index]
            tag = cls.url_to_docker_tag(image[index + len(index):])
            return f"{registry}:{tag}"

    @classmethod
    def url_to_nv(cls, url):
        url = cls.full_url(url)
        rr, tag = url.rsplit(':', 1)
        return cls.get_label_name(rr), cls.get_label_version(tag)

    @classmethod
    def entry(cls, url):
        image_full_url = cls.full_url(url)
        registry, repository_tag = image_full_url.split('/', 1)
        repository, tag = repository_tag.split(':')
        return dict(
            image=image_full_url,
            registry=registry,
            repository=repository,
            rr=f'{registry}/{repository}',
            tag=tag
        )

    @classmethod
    def build_fast(
            cls, path, images: dict, basic='', step='', base='', args=None, options='', context=None, push=True,
            push_only_last=False, remove=False):
        def _do_prepare(s, *pl):
            path_work = os.path.dirname(write_file('Dockerfile', s=s, t=True))
            for p in pl:
                if p and os.path.isdir(p):
                    for f in os.scandir(p):
                        if f.name.endswith('Dockerfile') or f.name == 'update':
                            continue
                        write_file(os.path.join(path_work, f.name), c=os.path.join(p, f.name))
            return path_work

        def _do_build(target, a, p):
            target = cls.real_image(target)
            build_args = ''
            if a:
                for k, v in a.items():
                    build_args += f' --build-arg "{k}={v}"'
            command = f'{cls.cli} build {options or ""} -t {target} {build_args} {p}'
            print('Run: ' + command, flush=True)
            shell_wrapper(command)

        def _do_build_build():
            env_map = {}
            td = tempfile.mkdtemp()
            for i, c in enumerate(content_build):
                image_build = f'build:cache--{i}'
                _do_build(image_build, args or {}, _do_prepare('\n'.join([content_args, c]), path, context))
                for image_nickname in images.keys():
                    fr, fd = f'/.dekartifacts/build/{image_nickname}/env', f'{td}/env.yaml'
                    remove_path(fd)
                    cls.cp(image_build, fr, fd, ignore=True)
                    if os.path.exists(fd):
                        env_map[image_nickname] = assign(env_map.get(image_nickname, {}), yaml.load(fd))
            result = {}
            for image_nickname in images.keys():
                result[image_nickname] = "\n" + "\n".join(
                    f'ENV {kk} {vv}' for kk, vv in env_map.get(image_nickname, {}).items()
                ) + "\n"
            return result

        def _do_build_result():
            for image_nickname in images.keys():
                last_image = None
                has_updated = False
                contents = content_result[image_nickname]
                for i, c in enumerate(contents):
                    is_last = i == len(contents) - 1
                    build_from = [f'FROM build:cache--{i} AS build{i}' for i in range(len(content_build))]
                    rlv_index = result_little_version[image_nickname].get(i, 0)
                    _args = {}
                    _image = images[image_nickname]
                    if not isinstance(_image, str):
                        _image, _args = _image
                    if is_last:
                        current_image = _image
                    elif i == 0:
                        current_image = f'{basic}:{base or "base"}-{image_nickname}-{rlv_index}'
                    else:
                        current_image = f'{basic}:{step or "step"}-{image_nickname}-{i}-{rlv_index}'
                    self_from = ''
                    if last_image:
                        self_from = f'FROM {last_image}'
                    last_image = current_image
                    if is_last or has_updated or not has_basic or not cls.remote_exists(current_image):
                        _do_build(
                            current_image,
                            {**(args or {}), **_args},
                            _do_prepare(
                                '\n'.join([
                                    content_args,
                                    *build_from, self_from, c, env_from_build[image_nickname] if i == 0 else ''
                                ]), path, context, os.path.join(path, image_nickname))
                        )
                        if push:
                            if not push_only_last or is_last:
                                cls.push(current_image)
                                if remove:
                                    cls.remove(current_image, safe=False)
                        has_updated = True

        has_basic = True
        if push_only_last:
            if not basic:
                has_basic = False
                basic = uuid.uuid4().hex
        else:
            if not basic:
                raise ValueError('When push_only_last=False, `basic` is needed')

        content_args = ''
        content_result = {}
        content_build_detail = {}
        result_little_version = {}
        for file in os.listdir(path):
            pa = os.path.join(path, file)
            if not file.startswith('.') and os.path.isdir(pa):
                content_result_detail = {}
                for file2 in os.listdir(pa):
                    pa2 = os.path.join(pa, file2)
                    if not file2.startswith('.') and os.path.isfile(pa2):
                        content = read_text(pa2)
                        if file2 == 'Dockerfile':
                            content_result_detail[0] = content
                        elif file2.endswith('.Dockerfile'):
                            name = file2.rsplit('.', 1)[0]
                            content_result_detail[int(name)] = content
                content_result[file] = [content_result_detail[i] for i in sorted(content_result_detail)]
                result_little_version[file] = {
                    i: int(x) for i, x in
                    enumerate(read_lines(os.path.join(pa, 'update'), default='', skip_empty=True))
                }
            elif file.endswith('.Dockerfile'):
                content = read_text(pa)
                if file.startswith('args.'):
                    content_args = content
                elif file.startswith('build.'):
                    name = '.'.join(file.split('.')[1:-1])
                    content_build_detail[int(name)] = content
        content_build = [content_build_detail[i] for i in sorted(content_build_detail)]
        env_from_build = _do_build_build()
        _do_build_result()

    @classmethod
    def static_build(cls, filepath, image):
        filename = os.path.basename(filepath)
        dockerfile = write_file(None, s=f'FROM scratch\nCMD ["sh"]\nCOPY {filename} /staticfiles/{filename}')
        image = cls.build(image, os.path.dirname(filepath), dockerfile=dockerfile)
        remove_path(dockerfile)
        return image

    @classmethod
    def static_fetch(cls, image, filepath=None):
        if not filepath:
            filepath = write_file(None)
        image = cls.pull(image)
        path_tmp = sure_dir(os.path.join(filepath, str(time.time())))
        cls.cp(image, '/staticfiles/.', path_tmp)
        filename = os.listdir(path_tmp)[0]
        result = os.path.join(filepath, filename)
        write_file(result, m=os.path.join(path_tmp, filename))
        remove_path(path_tmp)
        cls.remove(image)
        return result

    @classmethod
    def static_fetch_at(cls, image, filepath):
        filepath = normal_path(filepath)
        sure_parent_dir(filepath)
        remove_path(filepath)
        target = DockerArtifact.static_fetch(image, os.path.dirname(filepath))
        if target != filepath:
            write_file(filepath, m=target)
        return filepath
