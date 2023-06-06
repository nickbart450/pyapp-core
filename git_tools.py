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


def clone(url, path='./src', branch=None, auto_yes=False):
    path = str(path)
    path = os.path.abspath(path)

    if os.path.exists(path):
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
        repo = repository
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
    # clone run paramters: "https://<key>@github.com/SHR-nbartlett/WT_Plotter" -b "auto-update" -c "./src"
    parser = argparse.ArgumentParser(description='Do some git stuff')
    parser.add_argument('repo')

    parser.add_argument('-c, --clone', dest='clone', help='clone repo to specified path')

    parser.add_argument('-b, --branch', dest='branch', help='override default/main branch')

    args = parser.parse_args()
    if args.clone is not None:
        if args.branch is None or args.branch=="":
            rep = clone(args.repo, args.clone)
        else:
            rep = clone(args.repo, args.clone, branch=args.branch)

        if rep is None:
            sys.exit(1)
