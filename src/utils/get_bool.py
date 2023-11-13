import os

def get_boolean(key : str, default : str = "NO") -> bool:
    return bool(key.lower() in ('yes', 'y', '1', 't', 'true'))