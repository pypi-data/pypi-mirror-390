from .imports import *
def get_logFile(bpName: str = None, maxBytes: int = 100_000, backupCount: int = 3) -> logging.Logger:
    """
    If bpName is None, use the “caller module’s basename” as the logger name.
    Otherwise, use the explicitly provided bpName.
    """
    if bpName is None:
        # Find the first frame outside logging_utils.py
        frame_idx = _find_caller_frame_index()
        frame_info = inspect.stack()[frame_idx]
        caller_path = frame_info.filename  # e.g. "/home/joe/project/app/routes.py"
        bpName = os.path.splitext(os.path.basename(caller_path))[0]
        del frame_info

    log_dir = mkdirs("logs")
    log_path = os.path.join(log_dir, f"{bpName}.log")

    logger = logging.getLogger(bpName)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        try:
            handler = RotatingFileHandler(log_path, maxBytes=maxBytes, backupCount=backupCount)
            handler.setLevel(logging.INFO)

            fmt = "%(asctime)s - %(levelname)s - %(pathname)s - %(message)s"
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            console.setFormatter(formatter)
            logger.addHandler(console)
        except Exception as e:
            print(f"{e}")
    return logger

def _find_caller_frame_index():
    """
    Scan up the call stack until we find a frame whose module is NOT logging_utils.
    Return that index in inspect.stack().
    """
    for idx, frame_info in enumerate(inspect.stack()):
        # Ignore the very first frame (idx=0), which is this function itself.
        if idx == 0:
            continue
        module = inspect.getmodule(frame_info.frame)
        # If module is None (e.g. interactive), skip it;
        # else get module.__name__ and compare:
        module_name = module.__name__ if module else None

        # Replace 'yourpackage.logging_utils' with whatever your actual module path is:
        if module_name != __name__ and not module_name.startswith("logging"):
            # We found a frame that isn’t in this helper module or the stdlib logging.
            return idx
    # Fallback to 1 (the immediate caller) if nothing else matches:
    return 1
