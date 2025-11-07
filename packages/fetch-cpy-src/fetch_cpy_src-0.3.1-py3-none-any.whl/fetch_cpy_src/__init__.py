""" Fetch selected part of cpython source repository. """
__version__ = '0.3.1'
__all__ = [
    'fetch_manifest',
]

# imports
from pathlib import Path
from typing import List

# local imports
from fetch_cpy_src.manifest import Manifest


def fetch_manifest(manifest: Path, dst: Path = None) -> List[Path]:
    """ Fetch files listed in manifest to destinition directory. """
    if dst is None:
        dst = Path.cwd().resolve()

    fetched_files = Manifest.load(manifest, work_dir=dst).update()
    for _path in fetched_files:
        print('Fetched file: ', _path)

    return fetched_files
