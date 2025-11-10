import json
import os
import string
import functools
import tempfile
import subprocess
from urllib.parse import urlparse
from dektools.shell import shell_with_input_once, shell_wrapper, shell_output
from dektools.file import sure_dir, remove_path, write_file, read_text
from dektools.zip import decompress_files
from dektools.serializer.yaml import yaml
from dektools.web.url import Url
from .base import ArtifactBase


class HelmArtifact(ArtifactBase):
    typed = 'helm'
    cli_list = ['helm']

    @staticmethod
    def registry_to_repo(registry):
        valid = string.digits + string.ascii_letters
        result = ""
        for x in registry.split(":")[-1]:
            if x not in valid:
                x = '-'
            result += x
        return result.strip('- ')

    @classmethod
    def get_plugins(cls):
        result = shell_output(f"{cls.cli} plugin list")
        name_list = []
        for i, line in enumerate(result.splitlines()):
            if i == 0:
                continue
            name_list.append(line.split('\t', 1)[0].strip())
        return name_list

    @classmethod
    def url_to_docker_tag(cls, url):
        registry, chart, version = cls.url_parse(url)
        tag = urlparse(registry).path[1:].replace('/', '-') + '-' + chart + '-' + version
        tag = tag.strip('- ')
        return cls.normalize_docker_tag(url, tag)

    @classmethod
    def entry(cls, url):
        registry, chart, version = cls.url_parse(url)
        return dict(
            url=url,
            registry=registry,
            chart=chart,
            version=version
        )

    @property
    @functools.lru_cache(None)
    def path_repos(self):
        return os.path.join(self.path_work, 'repos.json')

    @staticmethod
    def get_chart_meta(path):
        return yaml.load(os.path.join(path, 'Chart.yaml'))

    def get_chart_path(self, chart, version):
        return os.path.join(self.path_objects, version, chart)

    def add_repo(self, registry, username=None, password=None):
        repos = []
        if os.path.exists(self.path_repos):
            repos = json.loads(read_text(self.path_repos))
        repo = self.registry_to_repo(registry)
        if repo in repos:
            return
        if username and password:
            ret, _, err = shell_with_input_once(
                f"{self.cli} repo add "
                f"--username {username} "
                f"--password-stdin {repo} {registry}",
                password)
            if ret:
                raise subprocess.SubprocessError(err)
        else:
            shell_wrapper(f'{self.cli} repo add {repo} "{registry}"')
        repos.append(repo)
        write_file(self.path_repos, s=json.dumps(repos))

    def imports(self, path_chart):
        path_out = None
        if os.path.isfile(path_chart):
            path_out = decompress_files(path_chart)
            path_chart = os.path.join(path_out, os.listdir(path_out)[0])
        chart_meta = self.get_chart_meta(path_chart)
        chart = chart_meta['name']
        version = chart_meta['version']
        write_file(self.get_chart_path(chart, version), c=path_chart)
        if path_out:
            remove_path(path_out)
        return chart_meta

    def package(self, chart, version):
        path_chart = self.get_chart_path(chart, version)
        path_tgz = os.path.join(os.getcwd(), f"{chart}-{version}.tgz")
        shell_wrapper(f"{self.cli} package {path_chart}")
        return write_file(None, t=True, m=path_tgz)

    def pull(self, url):
        raise NotImplementedError

    @classmethod
    def recognize(cls, url):
        return False

    @classmethod
    def login_all_env(cls, prepare=True, environ=None):
        return cls._login_all_env(prepare, environ, get_artifact_helm_by_url)


class HelmCommonArtifact(HelmArtifact):
    @classmethod
    def recognize(cls, url):  # https://localhost/path-before-index--yaml::chart-name:version
        return True

    def login(self, registry='', username='', password=''):
        print(F"Login to {registry} {username[0]}***{username[-1]}")
        self.add_repo(registry, username, password)

    def pull(self, url):
        registry, chart, version = self.url_parse(url)
        path_chart = self.get_chart_path(chart, version)
        sure_dir(path_chart)
        remove_path(path_chart)
        self.add_repo(registry)
        shell_wrapper(
            f'{self.cli} fetch {self.registry_to_repo(registry)}/{chart} '
            f'--version {version} --untar --untardir {os.path.dirname(path_chart)}'
        )
        shell_wrapper(f'{self.cli} dependency update {path_chart}')
        return path_chart


class HelmLocalArtifact(HelmArtifact):
    @classmethod
    def recognize(cls, url):
        return ':' not in url

    def pull(self, url):
        shell_wrapper(f'{self.cli} dependency update {url}')
        meta = self.get_chart_meta(url)
        path_chart = self.get_chart_path(meta['name'], meta['version'])
        write_file(path_chart, c=url)
        return path_chart


class HelmCodingArtifact(HelmCommonArtifact):
    @classmethod
    def recognize(cls, url):
        registry, _, _ = cls.url_parse(url, True)
        return urlparse(registry).netloc.endswith(".coding.net")

    @classmethod
    def prepare(cls):
        if 'coding-push' not in cls.get_plugins():
            shell_wrapper(f"{cls.cli} plugin install https://e.coding.net/coding-public/helm-push/helm-coding-push")

    def push(self, url):
        registry, chart, version = self.url_parse(url)
        path_tgz = self.package(chart, version)
        shell_wrapper(f"{self.cli} coding-push {path_tgz} {self.registry_to_repo(registry)}")
        remove_path(path_tgz)

    def push_batch(self, registry, charts):
        for chart, version in sorted(charts):
            self.push(f"{registry}::{chart}:{version}")


class HelmGitArtifact(HelmArtifact):
    @classmethod
    def recognize(cls, url):  # https://localhost/username/repo.git:/charts
        registry, _, _ = cls.url_parse(url, True)
        repo, rp_charts = cls.git_parse(registry)
        return urlparse(repo).netloc and rp_charts.startswith('/')

    @property
    @functools.lru_cache(None)
    def path_auth(self):
        return os.path.join(self.path_work, 'auth.json')

    @staticmethod
    def git_parse(registry):
        items = registry.rsplit(':', 1)
        if len(items) == 2:
            repo, rp_charts = items
        else:
            repo, rp_charts = items[0], ''
        return repo, rp_charts

    def login(self, registry='', email='', username='', password=''):
        self.login_auth(registry, email=email, username=username, password=password)

    def auth_from_local(self, registry):
        auth = self.get_auth(registry)
        if auth:
            email, username, password = auth['email'], auth['username'], auth['password']
            shell_wrapper(f'git config --local user.name "{username}"')
            shell_wrapper(f'git config --local user.email "{email}"')
            shell_wrapper(f'git config --local user.password "{password}"')

    def clone_repo(self, registry):
        repo, rp_charts = self.git_parse(registry)
        path_work = tempfile.mkdtemp()
        path_last = os.getcwd()
        os.chdir(path_work)
        auth = self.get_auth(registry)
        if auth:
            repo = Url.new(repo).replace(username=auth['username'], password=auth['password']).value
        shell_wrapper(f"git clone {repo}")
        path_repo = os.path.join(path_work, os.listdir(path_work)[0])
        os.chdir(path_repo)
        self.auth_from_local(registry)
        os.chdir(path_last)
        return path_repo, rp_charts

    def pull(self, url):
        registry, chart, version = self.url_parse(url)
        path_repo, rp_charts = self.clone_repo(registry)
        path_chart = self.get_chart_path(chart, version)
        write_file(path_chart, c=os.path.join(path_repo + rp_charts, chart))
        return path_chart

    def push_batch(self, registry, charts):
        path_repo, rp_charts = self.clone_repo(registry)
        path_last = os.getcwd()
        os.chdir(path_repo)
        for chart, version in sorted(charts):
            path_chart = self.get_chart_path(chart, version)
            write_file(os.path.join(path_repo + rp_charts, chart), c=path_chart)
        shell_wrapper(f"git add *")
        shell_wrapper(f'git commit -am "Add charts: {charts}"', False)
        shell_wrapper(f"git push")
        os.chdir(path_last)

    def push(self, url):
        registry, chart, version = self.url_parse(url)
        self.push_batch(registry, [(chart, version)])


def get_artifact_helm_by_url(url):
    for cls in [HelmGitArtifact, HelmCodingArtifact, HelmLocalArtifact, HelmCommonArtifact]:
        if cls.recognize(url):
            return cls
