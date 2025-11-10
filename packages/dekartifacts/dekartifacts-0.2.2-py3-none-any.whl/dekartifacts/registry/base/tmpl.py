from pathlib import Path
from dekgen.tmpl.generator import GeneratorFiles


class WhlGenerator(GeneratorFiles):
    TEMPLATE_DIR = Path(__file__).parent / 'templatefiles'
    template_name = 'whl'
