from dektools.file import write_file
from ..artifacts.docker import DockerArtifact
from .base.core import Registry


class DockerRegistry(Registry):
    def _pull(self, url, path):
        DockerArtifact.imports(path)

    def _push(self, url):
        result = DockerArtifact.exports([url], write_file(None))
        return next(iter(result.values()))

    def _get_nv(self, url, kwargs):
        return DockerArtifact.url_to_nv(url)
