import os
from dektools.serializer.yaml import yaml
from dektools.file import merge_assign
from dektools.shell import shell_wrapper


def helm_patch(path_chart, path_chart_patch):
    def _helm_patch_detail(operate, moment):
        if operate not in ['override', 'script']:
            raise ValueError(f'error operate: {operate}')
        if moment not in ['before', 'after']:
            raise ValueError(f'error moment: {moment}')
        if operate == 'override':
            fp = os.path.join(path_chart_patch, f'{operate}-{moment}-dep-update')
            if os.path.isdir(fp):
                merge_assign(path_chart, fp)
        elif operate == 'script':
            for shell, ext in [('bash', '.sh'), ('python3', '.py')]:
                fp = os.path.join(path_chart_patch, f'{operate}-{moment}-dep-update{ext}')
                if os.path.isfile(fp):
                    path_last = os.getcwd()
                    os.chdir(path_chart)
                    meta = yaml.load(os.path.join(path_chart, 'Chart.yaml'))
                    args = f""" "{meta['name']}" "{meta['version']}" "{meta.get('appVersion', '')}" """
                    shell_wrapper(f'{shell} {fp} {args}')
                    os.chdir(path_last)

    _helm_patch_detail('override', 'before')
    _helm_patch_detail('script', 'before')
    _helm_patch_detail('override', 'after')
    _helm_patch_detail('script', 'after')
