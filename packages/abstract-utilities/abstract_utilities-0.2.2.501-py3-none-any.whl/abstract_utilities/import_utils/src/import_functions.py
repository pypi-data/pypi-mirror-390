# --- auto-package bootstrap (run-safe) ---------------------------------
from ..imports import *
from .dot_utils import get_dot_range
from .sysroot_utils import get_sysroot
def clean_imports(imports,commaClean=True):
    chars=["*"]
    if not commaClean:
        chars.append(',')
    if isinstance(imports,str):
        imports = imports.split(',')
    return [eatElse(imp,chars=chars) for imp in imports if imp]
def get_cleaned_import_list(line,commaClean=True):
    cleaned_import_list=[]
    if IMPORT_TAG in line:
        imports = line.split(IMPORT_TAG)[1]
        cleaned_import_list+=clean_imports(imports,commaClean=commaClean)
    return cleaned_import_list
def get_module_from_import(imp,path=None):
    path = path or os.getcwd()
    i = get_dot_range(None,[imp])
    imp = eatAll(imp,'.')
    sysroot = get_sysroot(path,i)
    return os.path.join(sysroot, imp)

def safe_import(name: str, *, package: str | None = None, member: str | None = None, file: str | None = None):
    """
    Wrapper over importlib.import_module that:
    - if `name` is relative (starts with '.'), ensures `package` is set.
    - if `package` is missing, derives it from `file` (defaults to __file__).
    """
    file = file or __file__
    ensure_package_context(file)
    if name.startswith(".") and not package:
        
            
        pkg_name = get_module_from_import(name,path=None)
        # also set __package__ if we are running as a script
        if __name__ == "__main__" and (not globals().get("__package__")):
            globals()["__package__"] = pkg_name
        package = pkg_name

    mod = importlib.import_module(name, package=package)
    return getattr(mod, member) if member else mod



