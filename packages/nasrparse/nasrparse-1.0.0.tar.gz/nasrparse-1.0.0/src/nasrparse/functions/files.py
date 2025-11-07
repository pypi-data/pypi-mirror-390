from os import path


def check_file_exists(file_path: str) -> bool:
    if not path.exists(file_path):
        print(f"File at {file_path} not found")
        return False
    return True
