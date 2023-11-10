import os

def __get_boolean(key : str, default : str = "NO") -> bool:
    return bool(os.getenv(key, default).lower() in ('yes', 'y', '1', 't', 'true'))