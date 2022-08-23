from importlib import import_module
from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
ignore = ["utilities.py", "crawler_template.py", "archive.py"]
__all__ = [basename(f)[:-3] for f in modules if isfile(f)
           and not f.endswith('__init__.py') and basename(f) not in ignore]


for name in __all__:
    import_module("crawler."+name)
