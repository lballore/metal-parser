import os
import pkg_resources
import sys

from packaging import version
from pathlib import Path


def get_current_version():
    version = pkg_resources.require("metalparser")[0].version

    return version


def replace_version(current_version, new_version):
    files = [
        str(Path(os.path.dirname(os.path.abspath(__file__))).parent) + '/setup.py',
        str(Path(os.path.dirname(os.path.abspath(__file__))).parent) + '/docs/conf.py'
    ]
    current_version = get_current_version()

    for conf_file in files:
        fin = open(conf_file, "rt")
        data = fin.read()
        data = data.replace(current_version, new_version)
        fin.close()

        fin = open(conf_file, "wt")
        fin.write(data)
        fin.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit('No version specified')

    current_version = get_current_version()
    new_version = sys.argv[1]

    if version.parse(current_version) >= version.parse(new_version):
        sys.exit('New version is equal or precedent the current version: {} - {}'.format(current_version, new_version))
