import os
import sys
import shutil
import py7zr
from pyscreeps_arena.core import const, config
def CMD_NewProject():
    """
    cmd:
        pyscreeps-arena  [project_path]
        arena [project_path]

    * 复制"src" "game" "build.py" 到指定目录

    Returns:

    """
    if len(sys.argv) < 2:
        print("Usage: pyarena new [project_path]\n# or\narena new [project_path]")
        return
    project_path = sys.argv[1]
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    this_path = os.path.dirname(os.path.abspath(__file__))
    extract_7z(os.path.join(this_path, 'project.7z'), project_path)
    print("Project created at", project_path)


def extract_7z(file_path, output_dir):
    with py7zr.SevenZipFile(file_path, mode='r') as archive:
        archive.extractall(path=output_dir)


