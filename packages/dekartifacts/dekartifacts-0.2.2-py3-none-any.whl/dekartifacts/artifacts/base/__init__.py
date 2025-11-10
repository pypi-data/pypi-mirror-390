import os
import json
import hashlib
import string
from dektools.common import cached_property, cached_classproperty
from dektools.file import read_text, write_file
from dektools.str import decimal_to_short_str, slugify
from dektools.cfg import ObjectCfg
from dektools.env import query_env_map
from dektools.shell import Cli

docker_image_tag_max_length = 128


class ArtifactBase:
    typed = ''
    marker_registry = 'registry'

    cli_list = []
    url_seps = "::", ":"

    def __init__(self, environ=None):
        self.environ = environ or os.environ

    @classmethod
    def prepare(cls):
        pass

    @cached_classproperty
    def path_work(self):
        return ObjectCfg(__name__, 'basic', self.typed, module=True).path_dir

    @cached_classproperty
    def cli(self):
        return Cli(self.cli_list).cur

    @staticmethod
    def normalize_docker_tag(url, tag):
        if len(tag) > docker_image_tag_max_length:
            sha = decimal_to_short_str(
                int(hashlib.sha256(url.encode('utf-8')).hexdigest(), 16),
                string.digits + string.ascii_letters
            )
            sep = '-'
            tag = tag[len(tag) - docker_image_tag_max_length + len(sha) + len(sep):] + sep + sha
        return tag

    @classmethod
    def url_to_docker_tag(cls, url):
        return None

    @classmethod
    def url_join(cls, registry, name, version):
        return "".join([registry, cls.url_seps[0], name, cls.url_seps[1], version])

    @classmethod
    def url_parse(cls, url, ignore=False):
        ay = url.rsplit(cls.url_seps[0], 1)
        if len(ay) == 1:
            registry, name_and_version = ay[0], None
        else:
            registry, name_and_version = ay[0], ay[1]
        name, version = None, None
        if name_and_version:
            ay = name_and_version.split(cls.url_seps[1], 1)
            if len(ay) == 1:
                name, version = ay[0], None
            else:
                name, version = ay[0], ay[1]
        if not ignore and (not name or not version):
            raise ValueError(f"Invalid url: {url}")
        return registry, name, version

    def query_env_map(self, marker, is_end):
        return query_env_map(marker, is_end, self.environ)

    def list_env_registries(self):
        return sorted(self.query_env_map(f"__{self.typed}_{self.marker_registry}".upper(), True))

    def get_env_kwargs(self, registry=None):
        registry = registry or self.environ.get(f"{self.typed}_default_login_registry".upper(), "")
        return self.query_env_map(f"{registry}__{self.typed}_".upper(), False)

    def login_env(self, registry=None):
        kwargs = self.get_env_kwargs(registry)
        self.login(**kwargs)
        return kwargs

    def login(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def login_all_env(cls, prepare=True, environ=None):
        return cls._login_all_env(prepare, environ)

    @classmethod
    def _login_all_env(cls, prepare=True, environ=None, pick=None):
        ins = cls(environ)
        artifacts = {}
        for registry in ins.list_env_registries():
            kwargs = ins.get_env_kwargs(registry)
            if pick:
                c = pick(kwargs['registry'])
                artifact = artifacts[c] = c(environ)
            else:
                artifact = artifacts[cls] = ins
            artifact.login(**kwargs)
            if prepare:
                artifact.prepare()
        return artifacts

    @cached_property
    def path_objects(self):
        return os.path.join(self.path_work, 'objects')

    def path_keep_dir(self, path, path_object):
        sub = path_object[len(self.path_objects) + len(os.path.sep):]
        if path:
            return os.path.join(path, sub)
        return sub

    @cached_property
    def path_auth(self):
        return os.path.join(self.path_work, 'auth.json')

    def get_auth(self, registry):
        if os.path.exists(self.path_auth):
            auth = json.loads(read_text(self.path_auth))
            return auth.get(registry)

    def login_auth(self, registry='', **kwargs):
        auth = {}
        if os.path.exists(self.path_auth):
            auth = json.loads(read_text(self.path_auth))
        auth[registry] = kwargs
        write_file(self.path_auth, s=json.dumps(auth))

    @staticmethod
    def get_label_name(x):
        return slugify(x).replace('-', '_')

    @staticmethod
    def get_label_version(x):
        if all(char in set('.' + string.digits) for char in x):
            return x
        v = str(int.from_bytes(hashlib.sha256(x.encode('utf-8')).hexdigest(), byteorder='big', signed=False))
        lv = len(v)
        la = lv // 3
        return f"{v[0:la]}:{v[la + 1:la * 2]}.{v[la * 2 + 1]}"
