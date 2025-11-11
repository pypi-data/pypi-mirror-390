from ..imports import *
from .dot_utils import *

def ensure_on_path(p: Path):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
def get_sysroot(filepath,i):
    for j in range(i):
        filepath = os.path.dirname(filepath)
    return filepath

def get_dot_range_sysroot(filepath):
    sysroot = filepath
    while True:
        dot_range = get_dot_range(is_import_or_init(sysroot))
        if dot_range == 0:
            break
        sysroot = get_sysroot(sysroot,dot_range)
    
    return sysroot

def is_import_or_init(sysroot,likely=None):
    file_data = get_file_parts(sysroot)
    nuroot = sysroot
    dirname = file_data.get('dirname')
    if os.path.isdir(sysroot):
        dirname = sysroot
    ext = file_data.get('ext')
    filename = file_data.get('filename')
    
    candidates = []
    if likely:
        candidates += [os.path.join(dirname,f"{likely}.py"),os.path.join(dirname,likely)]
    candidates += [os.path.join(dirname,f"{filename}.py"),os.path.join(dirname,filename)]
    files: List[Path] = []
    for item in candidates:
        
        if os.path.exists(item):
            if os.path.isdir(item):
                
                nuroot=None
                init_name = '__init__.py'
                rootList = os.listdir(item)
                for basename in rootList:
                    if get_file_parts(basename,'filename') == filename:
                        nuroot = os.path.join(item,basename)
                        break
                if init_name in rootList:
                    nuroot = os.path.join(item,init_name)
                    break
                    
            else:
               nuroot=sysroot
               break

    return nuroot
