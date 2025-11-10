import time
from ...artifacts.docker import DockerArtifact


class AllInOneBase:
    artifact_all_in_one_cls = DockerArtifact
    artifact_src_cls = None

    def __init__(self, rr_all_in_one, environ=None):
        self.rr_all_in_one = rr_all_in_one
        self.artifact_all_in_one = self.artifact_all_in_one_cls(environ)
        self.artifact_src = self.artifact_src_cls(environ)

    @classmethod
    def prepare(cls):
        cls.artifact_all_in_one_cls.prepare()
        if cls.artifact_all_in_one_cls is not cls.artifact_src_cls:
            cls.artifact_src_cls.prepare()

    @classmethod
    def login_all_env(cls, prepare=True, environ=None):
        a = cls.artifact_all_in_one_cls.login_all_env(prepare, environ)
        if cls.artifact_all_in_one_cls is not cls.artifact_src_cls:
            b = cls.artifact_src_cls.login_all_env(prepare, environ)
        else:
            b = a
        return a, b

    def url_mage(self, url):
        return f"{self.rr_all_in_one}:{self.artifact_src.url_to_docker_tag(url)}"

    def push(self, items, interval=0):
        tags = self.artifact_all_in_one.remote_tags(self.rr_all_in_one)
        for i, item in enumerate(items):
            print(f"\npushing progress: {i + 1}/{len(items)} \nitem: {item}", flush=True)
            image = self.url_mage(item)
            if image.split(':')[-1] in tags:
                print(f"skip pushing as exist: {item}", flush=True)
                continue
            self.build(item, image)
            self.artifact_all_in_one.push(image)
            self.artifact_all_in_one.remove(image)
            self.remove(item)
            if interval:
                time.sleep(interval)

    def build(self, item, image):
        raise NotImplementedError

    def remove(self, item):
        pass

    def fetch(self, items, path, each=None):
        raise NotImplementedError
