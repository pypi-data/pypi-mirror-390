from ..artifacts.docker import DockerArtifact
from .base import AllInOneBase


class DockerAllInOne(AllInOneBase):
    artifact_src_cls = DockerArtifact

    def build(self, item, image):
        self.artifact_src.pull(item)
        self.artifact_src.tag(item, image)

    def remove(self, item):
        self.artifact_src.remove(item)

    def entry(self, url):
        return self.artifact_src.entry(self.url_mage(url))

    def fetch(self, items, path, each=None):
        self.exports(items, path)

    def pull(self, images, each=None):
        tags = self.artifact_all_in_one.remote_tags(self.rr_all_in_one)
        for image in images:
            if self.artifact_src.exist(image):
                pass
            elif tags is None or self.artifact_src.url_to_docker_tag(image) in tags:
                aio = self.url_mage(image)
                self.artifact_src.pull(aio)
                self.artifact_src.tag(aio, image)
                self.artifact_src.remove(aio)
            else:
                self.artifact_src.pull(image)
            if each:
                each(image)

    def exports(self, images, path):
        self.pull(images, lambda image: self.artifact_src.exports([image], path))
