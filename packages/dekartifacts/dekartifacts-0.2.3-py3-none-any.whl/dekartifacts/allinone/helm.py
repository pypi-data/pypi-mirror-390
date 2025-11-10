import os
import tempfile
from dektools.file import write_file, remove_path, sure_dir
from ..artifacts.helm import HelmCommonArtifact, HelmCodingArtifact, HelmGitArtifact, get_artifact_helm_by_url
from .base import AllInOneBase


class AllInOneHelm(AllInOneBase):
    def build(self, item, image):
        self.artifact_src.pull(item)
        _, chart, version = self.artifact_src.url_parse(item)
        path_file = self.artifact_src.package(chart, version)
        path_dir = os.path.dirname(path_file)
        path_docker = os.path.join(path_dir, 'Dockerfile')
        name_tgz = os.path.basename(path_file)
        write_file(path_docker, s=f'FROM scratch\nCMD ["sh"]\nCOPY {name_tgz} /charts/{name_tgz}')
        self.artifact_all_in_one.build(image, path_dir)
        remove_path(path_docker)
        remove_path(path_file)

    def fetch(self, items, path, each=None):
        sure_dir(path)
        tags = self.artifact_all_in_one.remote_tags(self.rr_all_in_one)
        for item in items:
            tag = self.artifact_src.url_to_docker_tag(item)
            if tags is None or tag in tags:
                image = self.artifact_all_in_one.pull(self.url_mage(item))
                pt = tempfile.mkdtemp()
                self.artifact_all_in_one.cp(image, '/charts/.', pt)
                self.artifact_all_in_one.remove(image)
                pz = os.path.join(pt, os.listdir(pt)[0])
                cm = self.artifact_src.imports(pz)
                remove_path(pt)
                path_object = self.artifact_src.get_chart_path(cm['name'], cm['version'])
            else:
                path_object = self.artifact_src.pull(item)
            chart_meta = self.artifact_src.get_chart_meta(path_object)
            if each:
                each(path_object, chart_meta, item)
            path_tgz = self.artifact_src.package(chart_meta['name'], chart_meta['version'])
            write_file(os.path.join(path, os.path.basename(path_tgz)), m=path_tgz)


class HelmCommonAllInOne(AllInOneHelm):
    artifact_src_cls = HelmCommonArtifact


class HelmCodingAllInOne(AllInOneHelm):
    artifact_src_cls = HelmCodingArtifact


class HelmGitAllInOne(AllInOneHelm):
    artifact_src_cls = HelmGitArtifact


def get_helm_all_in_one_by_url(url):
    artifact_helm = get_artifact_helm_by_url(url)
    for cls in [HelmCommonAllInOne, HelmCodingAllInOne, HelmGitAllInOne]:
        if cls.artifact_src_cls is artifact_helm:
            return cls
