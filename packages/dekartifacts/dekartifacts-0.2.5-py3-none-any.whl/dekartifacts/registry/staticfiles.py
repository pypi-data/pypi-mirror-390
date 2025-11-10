import os
from dektools.file import write_file
from ..artifacts.staticfiles import StaticfilesArtifact
from .base.core import Registry


class StaticfilesRegistry(Registry):
    def _pull(self, url, path):
        write_file(url, m=path)

    def _push(self, url):
        return url

    def _get_nv(self, url, kwargs):
        name = kwargs.get('name')
        if not name:
            name = StaticfilesArtifact.get_label_name(os.path.basename(url))
        return name, kwargs.get('version') or '0.1.0'
