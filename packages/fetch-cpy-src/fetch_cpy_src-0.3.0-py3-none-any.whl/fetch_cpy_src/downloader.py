""" download files of cpython repository """
# imports
from pathlib import Path
import time

from github import Github
from github.Repository import Repository


# shared constansts & variables
CPYTHON_REPO_OWNER = 'python'
CPYTHON_REPO_NAME = 'cpython'


def _get_cpython_repo(access_token: str = None) -> Repository:
    """ shared github repository access object """
    gh = Github(access_token) if access_token else Github()
    return gh.get_repo(f'{CPYTHON_REPO_OWNER}/{CPYTHON_REPO_NAME}')


def _download_cpython_file(repo: Repository, path: str, tag: str, target_dir: Path) -> Path:
    """ download file from cpython repository """
    # if the remote file does not exists, `github.GithubException.UnknownObjectException` would raise
    file_content = repo.get_contents(path, ref=tag)
    assert file_content.type == 'file'

    time.sleep(1)  # in case that exceed the github access limit

    # save it to target directory
    target_path = (target_dir / path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with target_path.open('wb+') as _bin_io:
        _bin_io.write(file_content.decoded_content)

    return target_path
    

def _download_cpython_dir(repo: Repository, path: str, tag: str, target_dir: Path) -> Path:
    """ download all files recursively of a directory from cpython repository """
    # if the remote file does not exists, `github.GithubException.UnknownObjectException` would raise
    dir_content = repo.get_contents(path, ref=tag)
    assert isinstance(dir_content, list)

    time.sleep(1)  # in case that exceed the github access limit

    # create path sub-directory within target directory
    target_path = (target_dir / path).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    # walk the path
    for _sub_content in dir_content:
        if _sub_content.type == 'dir':
            _download_cpython_dir(repo, _sub_content.path, tag, target_dir)

        else:  # _sub_content.type == 'file'
            _download_cpython_file(repo, _sub_content.path, tag, target_dir)

    return target_path
