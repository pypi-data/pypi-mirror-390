""" manifest to be downloaded & adapted """
# imports
import os
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Literal, List, Optional

import tomli  # builtin `tomlib` is available until 3.11
from github.Repository import Repository

# local imports
from fetch_cpy_src.downloader import _get_cpython_repo, _download_cpython_file, _download_cpython_dir
from fetch_cpy_src import adapter
from fetch_cpy_src.adapter import FileAdapter, DirAdapter, Adapter


@dataclass
class ManifestItem:
    """ Item of the manifest. 
    
    Item of both type "file" & "dir" can have both `file_adapters` & `dir_adapters`.
    For item of type "file", `dir_adapters` means those applied to the parent directory of
    the file; for item of type "dir", `file_adapters` means those applied to the sub-file 
    within the directory.
    """
    path: str
    rename: Optional[str]
    type: Literal['file', 'dir']
    file_adapters: List[FileAdapter]  # chain of adapters for file
    dir_adapters: List[DirAdapter]  # chain of adapters for file


def _inst_adapter(subcls_name: str) -> Adapter:
    """ instantiante a subclass of `Adapter` by its name """
    return getattr(adapter, subcls_name)()


class Manifest:
    """ manifest of files & directories of cpython repo to be downloaded & adapted """

    # class attributes
    github_access_token_env_var = 'GITHUB_ACCESS_TOKEN'

    # instance attributes
    _cpy_repo: Repository

    tag: str  # version in most cases
    items: List[ManifestItem]
    work_dir: Path  # download & inplace-adaption directory 

    def __init__(
        self, 
        tag: str, 
        items: List[ManifestItem], 
        work_dir: Path = None, 
        github_access_token: str = None
    ):
        """ constructor """
        self.tag = tag
        self.items = items
        self.work_dir = (work_dir if work_dir else Path.cwd()).resolve()

        # read `github_access_token` from env
        self._cpy_repo = _get_cpython_repo(access_token=github_access_token)

    @classmethod
    def load(cls, toml_file: Path, work_dir: Path = None, github_access_token: Optional[str] = None) -> 'Manifest':
        """ create manifest from toml """
        # read toml file
        toml_file = toml_file.resolve()
        with toml_file.open('rb') as _f:
            toml_dict = tomli.load(_f)

        items = []
        for _item_dict in toml_dict['items']:
            rename = _item_dict.get('rename', None)
            file_adapters = _item_dict.get('file_adapters', [])
            dir_adapters = _item_dict.get('dir_adapters', [])

            item = ManifestItem(
                path=_item_dict['path'],
                rename=rename,
                type=_item_dict['type'],
                file_adapters=[_inst_adapter(ad) for ad in file_adapters],  # type: ignore[misc]
                dir_adapters=[_inst_adapter(ad) for ad in dir_adapters],  # type: ignore[misc]
            )  
            items.append(item)

        # read env for access token
        if not github_access_token:
            github_access_token = os.getenv(cls.github_access_token_env_var, None)
            
        return cls(
            tag=toml_dict['tag'],
            items=items,
            work_dir=work_dir,
            github_access_token=github_access_token
        )

    def update(self) -> List[Path]:
        """ apply downloading & adaption, return proceeded files' path """
        updated_list: List[Path] = []

        # DO NOT merge downloading & adapting loop! For some adatption need work correctly when related 
        # downloading completed (like top-level-script adaption). Besides, the developer can test adaption
        # alone without downloadnig.

        # download
        for _item in self.items:
            # for file
            if _item.type == 'file':
                target_file = _download_cpython_file(self._cpy_repo, _item.path, self.tag, self.work_dir)
                if rename := _item.rename:
                    shutil.move(target_file, self.work_dir / rename)

            elif _item.type == 'dir':
                target_dir = _download_cpython_dir(self._cpy_repo, _item.path, self.tag, self.work_dir)
                if rename := _item.rename:
                    shutil.move(target_dir, self.work_dir / rename)
                    shutil.rmtree(self.work_dir / _item.path.split('/')[0])

        # adaption
        for _item in self.items:
            _path = _item.path if _item.rename is None else _item.rename

            # for file
            if _item.type == 'file':
                target_file = (self.work_dir / _path).resolve()
                target_dir = target_file.parent

                for _dir_adapter in _item.dir_adapters:
                    # chained
                    target_dir = _dir_adapter.adapt(target_dir, in_place=True, dst_dir=target_dir)  # type: ignore[assignment]
                    if target_dir is None:
                        break

                for _adapter in _item.file_adapters:
                    # chained
                    target_file = _adapter.adapt(target_file, in_place=True, dst_file=target_file)  # type: ignore[assignment]
                    if target_dir is None:
                        break

                    updated_list.append(target_file)

            # for directory
            elif _item.type == 'dir':
                target_dir = (self.work_dir / _path).resolve()
                
                for _dir_adapter in _item.dir_adapters:
                    # chained
                    target_dir = _dir_adapter.adapt(target_dir, in_place=True, dst_dir=target_dir)  # type: ignore[assignment]
                    if target_dir is None:
                        break

                for _sub_dir, _folders, _files in os.walk(target_dir.resolve()):
                    _ = _folders
                    sub_dir = Path(_sub_dir)

                    for _file_name in _files:
                        target_file = sub_dir / _file_name

                        for _adapter in _item.file_adapters:
                            # chained
                            target_file = _adapter.adapt(target_file, in_place=True, dst_file=target_file)  # type: ignore[assignment]
                            if target_file is None:
                                break

                            updated_list.append(target_file)

        return updated_list
