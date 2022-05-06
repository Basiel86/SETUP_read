import os.path
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    SRV_path = f"d:\WORK\###\SRV_path"

    print(os.path.isdir(SRV_path))

    with open(f"{SRV_path}\\Server config folder path.txt", 'w') as file:
        file.write(SRV_path)


def is_srv_list_exist():
    srv_path_file_name = "Server config folder path.txt"
    srv_path_file_path = resource_path(srv_path_file_name)
    if not os.path.exists(srv_path_file_path):
        with open(srv_path_file_path, 'w') as file:
            file.write("SRV_path")
    return srv_path_file_path


def get_srv_path():
    srv_path_file_path = is_srv_list_exist()
    with open(srv_path_file_path) as f:
        lines = f.read()
        first = lines.split('\n', 1)[0]
    if os.path.exists(first):
        return first
    else:
        return None


if __name__ == '__main__':
    print(get_srv_path())
