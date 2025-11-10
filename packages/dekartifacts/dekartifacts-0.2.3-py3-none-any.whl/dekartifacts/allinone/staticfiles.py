from dektools.file import write_file, remove_path, sure_dir
from ..artifacts.staticfiles import StaticfilesArtifact
from .base import AllInOneBase


class StaticfilesAllInOne(AllInOneBase):
    artifact_src_cls = StaticfilesArtifact

    def build(self, item, image):
        filepath = self.artifact_src.pull(item)
        self.artifact_all_in_one.static_build(filepath, image)
        remove_path(filepath)

    def fetch(self, items, path, each=None):
        sure_dir(path)
        tags = self.artifact_all_in_one.remote_tags(self.rr_all_in_one)
        for item in items:
            tag = self.artifact_src.url_to_docker_tag(item)
            if tags is None or tag in tags:
                filepath = self.artifact_all_in_one.static_fetch(self.url_mage(item))
                path_object = self.artifact_src.imports(filepath, clone=False)
                remove_path(filepath)
            else:
                path_object = self.artifact_src.pull(item)
            if each:
                each(path_object, item)
            write_file(self.artifact_src.path_keep_dir(path, path_object), m=path_object)
