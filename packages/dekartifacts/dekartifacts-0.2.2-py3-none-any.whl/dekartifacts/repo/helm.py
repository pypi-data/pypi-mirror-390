import os
from collections import OrderedDict
from dektools.time import now
from dektools.serializer.yaml import yaml
from dektools.file import write_file, sure_dir, clear_dir, remove_path
from dektools.zip import compress_files
from dektools.hash import hash_file
from ..artifacts.helm import HelmArtifact, get_artifact_helm_by_url


def create_helm_repo(url_base, repos, path_out=None):
    if path_out:
        clear_dir(sure_dir(path_out))
    else:
        path_out = write_file(None)
    index_data = OrderedDict([('apiVersion', 'v1'), ('entries', OrderedDict()), ('generated', _now())])
    for repo in repos:
        helm_artifact_cls = get_artifact_helm_by_url(repo)
        helm_artifact = helm_artifact_cls()
        path = helm_artifact.pull(repo)
        meta = HelmArtifact.get_chart_meta(path)
        filename = f"{meta['name']}-{meta['version']}.tgz"
        url = f"{url_base}/{filename}"
        target = os.path.join(path_out, filename)
        path_tmp = write_file(None)
        write_file(os.path.join(path_tmp, meta['name']), m=path)
        compress_files(path_tmp, target, typed='tgz')
        remove_path(path_tmp)
        meta['digest'] = hash_file('sha256', target)
        meta['created'] = _now()
        meta['urls'] = [url]
        items = index_data['entries'].setdefault(meta['name'], [])
        if not next(iter(x for x in items if x['version'] == meta['version']), None):
            items.append(meta)
    write_file(os.path.join(path_out, 'index.yaml'), s=yaml.dumps(index_data))
    write_file(os.path.join(path_out, 'index.html'), s="""<a href="./index.yaml">index.yaml</a>""")
    return path_out


def _now():
    t = now()
    return f"{t.strftime('%Y-%m-%dT%H:%M:%S')}.{t.microsecond:06d}000Z"
