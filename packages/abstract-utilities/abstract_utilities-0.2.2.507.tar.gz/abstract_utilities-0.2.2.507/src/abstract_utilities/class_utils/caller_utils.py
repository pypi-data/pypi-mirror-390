from .imports import *
def get_caller(i: Optional[int] = None) -> str:
    """
    Return the filename of the calling frame.

    Args:
        i: Optional stack depth offset. 
           None = immediate caller (depth 1).

    Returns:
        Absolute path of the file for the stack frame.
    """
    depth = 1 if i is None else int(i)
    stack = inspect.stack()
    if depth >= len(stack):
        depth = len(stack) - 1
    return stack[depth].filename


def get_caller_path(i: Optional[int] = None) -> str:
    """
    Return the absolute path of the caller's file.
    """
    depth = 1 if i is None else int(i)
    file_path = get_caller(depth + 1)
    return os.path.realpath(file_path)


def get_caller_dir(i: Optional[int] = None) -> str:
    """
    Return the absolute directory of the caller's file.
    """
    depth = 1 if i is None else int(i)
    abspath = get_caller_path(depth + 1)
    return os.path.dirname(abspath)
