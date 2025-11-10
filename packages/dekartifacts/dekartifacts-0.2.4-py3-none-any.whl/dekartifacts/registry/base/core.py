import os
import sys
import virtualenv
from twine.package import _safe_name
from dektools.zip import compress_files
from dektools.file import write_file, remove_path
from dektools.shell import shell_wrapper, shell_output, shell_result
from dektools.cfg import ObjectCfg
from dektools.common import cached_property
from dektools.venvx.tools import find_venv_bin
from dektools.web.url import Url
from dektools.env import query_env_map
from dektools.str import Fragment
from .tmpl import WhlGenerator

module_name = __name__.partition('.')[0]


class Registry:
    @classmethod
    def login_all_env(cls):
        for name in sorted(query_env_map(f"__REGISTRY_REGISTRY".upper(), True)):
            data = query_env_map(f"{name.upper()}__REGISTRY", False)
            cls(data.pop('registry')).login(name=name, **data)

    def __init__(self, registry_url, namespace='default'):
        self.url = registry_url
        self.namespace = namespace

    @cached_property
    def cfg(self):
        return ObjectCfg(__name__, 'registry', module=True, default=list)

    @property
    def auth_url(self):
        item = self.item.copy()
        registry = item.pop('registry')
        item.pop('name', None)
        return Url.new(registry).update(**item).value

    @property
    def item(self):
        items = self.cfg.get()
        for item in items:
            if item['name'] == self.url or item['registry'] == self.url:
                return item
        return {'registry': self.url}

    def find_item(self, name):
        items = self.cfg.get()
        for i, item in enumerate(items):
            if item['name'] == name or item['registry'] == name:
                return i, items
        return -1, items

    def logoff(self, name=None):
        name = name or self.url
        index, items = self.find_item(name)
        if index == -1:
            return False
        else:
            items.pop(index)
            self.cfg.set(items)
            return True

    def login(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v not in {'', None}}
        index, items = self.find_item(kwargs['name'])
        item = dict(**kwargs, registry=self.url)
        if index == -1:
            items.append(item)
        else:
            items[index] = item
        self.cfg.set(items)
        return self

    def _push(self, url):
        raise NotImplementedError()

    def _pull(self, url, path):
        raise NotImplementedError()

    def _get_nv(self, url, kwargs):
        raise NotImplementedError()

    def _get_nv_final(self, url, kwargs):
        name, version = self._get_nv(url, kwargs)
        return f"{module_name}_{self.namespace}_{name}".lower(), version

    def exist(self, url, **kwargs):
        name, version = self._get_nv_final(url, kwargs)
        rc, content = shell_result(f"pip index versions {name} --index-url {self.auth_url}")
        if rc:
            return False
        s = Fragment(content, f"Available versions: ", sep=True)[2]
        index = s.find('\n')
        if index != -1:
            s = s[:index]
        versions = s.strip().split(', ')
        return version in versions

    def push(self, url, **kwargs):
        name, version = self._get_nv_final(url, kwargs)
        file = generate_whl(self._push(url), name, version)
        item = self.item
        os.environ['TWINE_USERNAME'] = item['username']
        os.environ['TWINE_PASSWORD'] = item['password']
        shell_wrapper(
            f'{sys.executable} -m twine upload "{file}" --verbose --repository-url {item["registry"]}')
        remove_path(file)

    def pull(self, url, **kwargs):
        name, version = self._get_nv_final(url, kwargs)
        path_tmp = write_file(None)
        path_venv = os.path.join(path_tmp, ".venv")
        virtualenv.cli_run([path_venv])
        path_python = find_venv_bin('python', path_tmp)
        shell_wrapper(
            f'{path_python} -m pip install --no-cache-dir --index-url {self.auth_url} {_safe_name(name)}=={version}')
        path_dir = os.path.dirname(shell_output(f'{path_python} -c "import {name};print({name}.__file__)"'))
        path_target = take_target(path_dir)
        self._pull(url, path_target)
        remove_path(path_tmp)


def generate_whl(path_src, name, version, path_out=None):
    if path_out is None:
        path_out = write_file(None)
    filename = f'{name}-{version}-py3-none-any.whl'
    path_out_tmp = os.path.join(path_out, filename + '.tmp')
    WhlGenerator(path_out_tmp, True, dict(
        name=name,
        safe_name=_safe_name(name),
        version=version,
        filename=os.path.basename(path_src),
    )).action()
    path_target = os.path.join(path_out_tmp, name, 'assets', os.path.basename(path_src))
    write_file(path_target, c=path_src)
    path_result = compress_files(path_out_tmp, os.path.join(path_out, filename))
    remove_path(path_out_tmp)
    return path_result


def take_target(path):
    path_assets = os.path.join(path, 'assets')
    return os.path.join(path_assets, os.listdir(path_assets)[0])
