from ..imports import *
from .pkg_utils import *

def get_text_or_read(text=None,file_path=None):
    text = text or ''
    imports_js = {}
    if not text and file_path and os.path.isfile(file_path):
        text=read_from_file(file_path)
    return text
def is_line_import(line):
    if line and (line.startswith(FROM_TAG) or line.startswith(IMPORT_TAG)):
        return True
    return False
def is_line_group_import(line):
    if line and (line.startswith(FROM_TAG) and IMPORT_TAG in line):
        return True
    return False

def is_from_line_group(line):
    if line and line.startswith(FROM_TAG) and IMPORT_TAG in line and '(' in line:
        import_spl = line.split(IMPORT_TAG)[-1]
        import_spl_clean = clean_line(line)
        if not import_spl_clean.endswith(')'):
            return True
    return False

def get_all_imports(text=None,file_path=None,import_pkg_js=None):
    if text and os.path.isfile(text):
        file_path = text
        text = read_from_file(text)    
    text = get_text_or_read(text=text,file_path=file_path)
    lines = text.split('\n')
    cleaned_import_list=[]
    nu_lines = []
    is_from_group = False
    import_pkg_js = ensure_import_pkg_js(import_pkg_js,file_path=file_path)
    for line in lines:
        if line.startswith(IMPORT_TAG) and ' from ' not in line:
            cleaned_import_list = get_cleaned_import_list(line)
            import_pkg_js = add_imports_to_import_pkg_js("import",cleaned_import_list,import_pkg_js=import_pkg_js)
        else:
            if is_from_group:
                import_pkg=is_from_group
                line = clean_line(line)
                if line.endswith(')'):
                   is_from_group=False
                   line=line[:-1]
                imports_from_import_pkg = clean_imports(line)
                import_pkg_js = add_imports_to_import_pkg_js(import_pkg,imports_from_import_pkg,import_pkg_js=import_pkg_js)
                
            else:
                import_pkg_js=update_import_pkg_js(line,import_pkg_js=import_pkg_js)
            if is_from_line_group(line) and is_from_group == False:
                is_from_group=get_import_pkg(line)
    return import_pkg_js

def clean_imports(text=None,file_path=None,import_pkg_js=None,fill_nulines=False):
    if text and os.path.isfile(text):
        file_path = text
        text = read_from_file(text)    
    if not import_pkg_js:
        import_pkg_js = get_all_imports(text=text,file_path=file_path)
    import_pkg_js = ensure_import_pkg_js(import_pkg_js,file_path=file_path)
    nu_lines = import_pkg_js["context"]["nulines"]
    for pkg,values in import_pkg_js.items():
        comments = []
        if pkg not in ["context"]: 
            
            imports = values.get('imports')
            for i,imp in enumerate(imports):
                if '#' in imp:
                    imp_spl = imp.split('#')
                    comments.append(imp_spl[-1])
                    imports[i] = clean_line(imp_spl[0])
            imports = list(set(imports))   
            if '*' in imports:
                imports="*"
            else:
                imports=','.join(imports)
                if comments:
                    comments=','.join(comments)
                    imports+=f" #{comments}"
            import_pkg_js[pkg]["imports"]=imports
            if fill_nulines:
                line = values.get('line')
                if len(nu_lines) >= line:
                    nu_lines[line] += imports
    return import_pkg_js
def clean_all_imports(text=None,file_path=None,import_pkg_js=None,fill_nulines=False):
    clean_imports(text=text,file_path=file_path,import_pkg_js=import_pkg_js,fill_nulines=import_pkg_js)
    import_pkg_js["context"]["nulines"]=nu_lines
    return import_pkg_js
def get_clean_import_string(import_pkg_js,fill_nulines=False,get_locals=False):
    import_pkg_js = clean_imports(import_pkg_js=import_pkg_js,fill_nulines=fill_nulines)
    import_ls = []
    for key,values in import_pkg_js.items():
        if key not in ['context','nulines']:
            imports = None
            imp_values= values.get('imports')
            if key == 'import':
                imports = f'import {imp_values}'
            elif get_locals or not key.startswith('.'):
                imports = f'from {key} import {imp_values}'
            if imports:
                import_ls.append(imports)
    return '\n'.join(import_ls)
def get_clean_imports_from_files(files):
    import_pkg_js={}
    for file in files:
        import_pkg_js = get_all_imports(file,import_pkg_js=import_pkg_js)
    return get_clean_import_string(import_pkg_js)
def get_dot_fro_line(line,dirname):
    from_line = line.split(FROM_TAG)[-1]
    dot_fro = ""
    for char in from_line:
        if  char != '.':
            line = f"from {dot_fro}{eatAll(from_line,'.')}"
            break
        dirname = os.path.dirname(dirname)
        dirbase = os.path.basename(dirname)
        dot_fro = f"{dirbase}.{dot_fro}"
    return line
def get_dot_fro_lines(lines,file_path,all_imps):
    for line in lines:
        if line.startswith(FROM_TAG):
            line = get_dot_fro_line(line,file_path)
            if line in all_imps:
                line = ""
        if line:
            all_imps.append(line)
    return all_imps
def get_all_real_imps(text=None,file_path=None,all_imps=None):
    if text and os.path.isfile(text):
        file_path = text
        text = read_from_file(text)    
    all_imps = all_imps or []
    contents = get_text_or_read(text=text,file_path=file_path)
    lines = contents.split('\n')
    all_imps = get_dot_fro_lines(lines,file_path,all_imps)
    return '\n'.join(all_imps)
def save_cleaned_imports(text=None,file_path=None,write=False,import_pkg_js=None):
    import_pkg_js=get_all_imports(text=text,file_path=file_path,import_pkg_js=import_pkg_js)
    import_pkg_js = clean_all_imports(text=text,file_path=file_path,import_pkg_js=import_pkg_js)
    contents = '\n'.join(import_pkg_js["context"]["nulines"])
    if file_path and write:
        write_to_file(contents=contents,file_path=file_path)
    return contents
