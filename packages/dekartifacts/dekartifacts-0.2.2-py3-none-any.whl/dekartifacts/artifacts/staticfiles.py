import os
from urllib.parse import urlparse
from dektools.file import write_file
from dektools.download import download_tree_from_http, download_http_exist
from dektools.str import replace
from .base import ArtifactBase


class StaticfilesArtifact(ArtifactBase):
    typed = 'staticfiles'

    @classmethod
    def url_to_docker_tag(cls, url):
        tag = replace(urlparse(url).path, {k: '-' for k in ['/', '\\']}).strip('-')
        return cls.normalize_docker_tag(url, tag)

    @classmethod
    def recognize(cls, url):
        return False

    @classmethod
    def login_all_env(cls, prepare=True, environ=None):
        return cls._login_all_env(prepare, environ, get_artifact_staticfiles_by_url)

    def login(self, registry='', username='', password=''):
        self.login_auth(urlparse(registry).netloc, username=username, password=password)

    def imports(self, path_file, path_dir=None, clone=True):
        if path_dir:
            sub = path_file[len(path_dir) + len(os.path.sep):]
        else:
            sub = os.path.basename(path_file)
        path_object = os.path.join(self.path_objects, sub)
        write_file(path_object, **{'c' if clone else 'm': path_file})
        return path_object

    def pull(self, url):
        auth = self.get_auth(urlparse(url).netloc) or {}
        return os.path.join(
            self.path_objects, download_tree_from_http(
                self.path_objects, [url], **auth
            )[url]
        )

    def exist(self, url):
        auth = self.get_auth(urlparse(url).netloc) or {}
        return download_http_exist(url, **auth)


class StaticfilesCommonArtifact(StaticfilesArtifact):
    @classmethod
    def recognize(cls, url):
        return True


class StaticfilesLocalArtifact(StaticfilesArtifact):
    @classmethod
    def recognize(cls, url):
        return ':' not in url

    def pull(self, url):
        result = os.path.join(self.path_objects, os.path.basename(url))
        write_file(result, c=url)
        return result

    def exist(self, url):
        return os.path.exists(url)


class StaticfilesRepoArtifact(StaticfilesArtifact):  # https://localhost/path_of_base::name:version
    @classmethod
    def recognize(cls, url):
        return cls.url_seps[0] in url

    def pull(self, url):
        from ..repo.staticfiles import fetch_staticfiles_item

        registry, name, version = self.url_parse(url, ignore=True)
        auth = self.get_auth(urlparse(registry).netloc) or {}
        return fetch_staticfiles_item(registry, name, version, self.path_objects, **auth)

    def exist(self, url):
        from ..repo.staticfiles import exist_staticfiles_item

        registry, name, version = self.url_parse(url)
        auth = self.get_auth(urlparse(registry).netloc) or {}
        return exist_staticfiles_item(registry, name, version, **auth)


def get_artifact_staticfiles_by_url(url):
    for cls in [StaticfilesRepoArtifact, StaticfilesLocalArtifact, StaticfilesCommonArtifact]:
        if cls.recognize(url):
            return cls
