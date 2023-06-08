import sys

from Settings import Settings

import pygit2
import shutil
import argparse
import re
import os
import stat

SETTINGS = Settings(os.getcwd())
SETTINGS.file = os.path.normpath(os.path.join(os.getcwd(), "install_settings.json"))
SETTINGS.read_settings()

token = SETTINGS.git['key']

pygit2.option(pygit2.GIT_OPT_SET_OWNER_VALIDATION, 0)  # Disables ownership verification

default_clone_dir = './src'

def isnear(value, reference, dist):
    if value is None or reference is None:
        return False

    if abs(reference-value) <= dist:
        return True
    else:
        return False


class MyRemoteCallbacks(pygit2.RemoteCallbacks):
    def __init__(self):
        super().__init__(pygit2.UserPass(token, 'x-oauth-basic'))
        self.progress = 0
        self.progress_steps = [0, 5, 10, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

    def transfer_progress(self, stats):
        self.progress = int(100*(stats.indexed_objects/stats.total_objects))
        for p in self.progress_steps:
            if isnear(self.progress, p, 0.49):
                print('Download Progress: {}%'.format(self.progress))
                self.progress_steps[self.progress_steps.index(self.progress)] = None


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def clone_args(argparse_args):
    """Breaks down argparse command-line arguments to pass to main clone function"""
    url = argparse_args.repo_url
    path = argparse_args.clone
    branch = argparse_args.branch
    auto_yes = argparse_args.yes
    repository = clone(url, path=path, branch=branch, auto_yes=auto_yes)
    return repository


def clone(url, path=default_clone_dir, branch=None, auto_yes=False):
    path = str(path)
    path = os.path.abspath(path)

    # If directory exists and is not empty
    if os.path.exists(path) and len(os.listdir(path))>0:
        if auto_yes:
            shutil.rmtree(path, onerror=onerror)
        else:
            print('Directory conflict! {}'.format(path))
            ans = input('Delete conflicting directory? (Y/N): ')
            if 'y' in ans.lower():
                shutil.rmtree(path, onerror=onerror)
            else:
                print('Cancelling clone operation')
                # in the future, should offer alternatives
                return

    url = str(url).replace('\\', '/')
    display_url = url
    if "<key>" in url:
        url = url.replace('<key>', token)

    cb = MyRemoteCallbacks()
    if branch is None:
        print("Cloning {}".format(display_url))
        R = pygit2.clone_repository(url, path, callbacks=cb)
    else:
        branch = str(branch)
        print("Cloning '{}' branch from: {}\n".format(branch, display_url))
        R = pygit2.clone_repository(url, path, checkout_branch=branch, callbacks=MyRemoteCallbacks())
    return R


def fetch(repository=None):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    remotes = repo.remotes
    if len(remotes) > 0 and remotes[0] is not None:
        remote = remotes['origin']
        remote.fetch(callbacks=MyRemoteCallbacks(), message='tags')
        return remote
    else:
        return


def tags(repository=None, ignore_rc=True):
    if repository is not None:
        if os.path.exists(os.path.abspath(repository)):
            repo = pygit2.Repository(pygit2.discover_repository(os.path.abspath(repository)))
            # print(repo.config.__contains__('safe.directory'))

        elif isinstance(repository, pygit2.Repository):
            repo = repository
        else:
            raise RuntimeError('Provided repository is not valid git repo')

    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    regex = re.compile('^refs/tags/')
    tag_list = [r.strip('refs/tags/') for r in repo.references if regex.match(r)]

    if ignore_rc:
        for t in tag_list:
            if 'rc' in t:
                tag_list.pop(tag_list.index(t))

    return tag_list


def current_version(repository=None):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    return repo.describe(describe_strategy=1).split('-')[0]  # 1=GIT_DESCRIBE_TAGS


def install_version(version, repository=None):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))

    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    repo_tags = tags(repo)
    if str(version) in repo_tags:
        repo.reset(version, reset_type=2)  # 2=GIT_RESET_HARD


def pull(repository=None, branch='main'):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    remote_master_id = repo.lookup_reference('refs/remotes/origin/{}'.format(branch)).target
    repo.checkout_tree(repo.get(remote_master_id))
    master_ref = repo.lookup_reference('refs/heads/{}'.format(branch))
    master_ref.set_target(remote_master_id)
    repo.head.set_target(remote_master_id)


if __name__ == '__main__':
    # clone run parameters: clone -b "auto-update" "https://<key>@github.com/SHR-nbartlett/WT_Plotter"

    # Top Level Parser
    parser = argparse.ArgumentParser(description='Do some git stuff')
    parser.add_argument('-y', '--yes', dest='yes', default=False, action='store_true')
    subparsers = parser.add_subparsers(help='Commands help')

    # create the parser for the "clone" command
    parser_clone = subparsers.add_parser('clone', help='clone help')

    parser_clone.add_argument('repo_url', nargs='?', help='source repository or url to clone')
    dest_help_str = 'clone repo to specified path. Path should be valid, empty directory. Default: ./src'
    parser_clone.add_argument('-d', '--dest', dest='clone', nargs='?', default=default_clone_dir, help=dest_help_str)
    parser_clone.add_argument('-b, --branch', dest='branch', nargs='?', help='override default/main branch')
    parser_clone.set_defaults(func=clone_args)

    args = parser.parse_args()
    args.func(args)
