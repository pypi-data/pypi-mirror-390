import re
import os
from dektools.file import write_file, remove_path
from dektools.zip import compress_files
from ..artifacts.helm import HelmCommonArtifact
from .base.core import Registry


class HelmRegistry(Registry):
    def _pull(self, url, path):
        write_file(url, m=path)

    def _push(self, url):
        if os.path.isdir(url):
            chart_meta = HelmCommonArtifact.get_chart_meta(url)
            name = chart_meta['name']
            version = chart_meta['version']
            self.__push_temp = compress_files(url, write_file(f"{name}-{version}.tgz", t=True))
            return self.__push_temp
        return url

    def push(self, url, **kwargs):
        super().push(url, **kwargs)
        remove_path(self.__push_temp)
        del self.__push_temp

    def _get_nv(self, url, kwargs):
        if os.path.isdir(url):
            chart_meta = HelmCommonArtifact.get_chart_meta(url)
            name = chart_meta['name']
            version = chart_meta['version']
        else:
            s = os.path.splitext(os.path.basename(url))[0]
            index = re.search('[0-9]+.[0-9]+.[0-9]+.', s).span()[0]
            name = s[:index - 1]
            version = s[index:]
        return name, version
