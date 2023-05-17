from Settings import Settings

import pygit2
import argparse
import re
import os

print('CWD', os.getcwd())

SETTINGS = Settings(os.getcwd())
SETTINGS.file = os.path.normpath(os.path.join(os.getcwd(), "install_settings.json"))
SETTINGS.read_settings()

token = SETTINGS.git['key']


class MyRemoteCallbacks(pygit2.RemoteCallbacks):
    def __init__(self):
        super().__init__(pygit2.UserPass(token, 'x-oauth-basic'))

    def transfer_progress(self, stats):
        print(f'{stats.indexed_objects}/{stats.total_objects}')


def clone(url, path='./src', branch=None):
    path = str(path)

    url = str(url).replace('\\', '/')
    display_url = url
    if "<key>" in url:
        url = url.replace('<key>', token)
    print("Cloning {}".format(display_url))
    print("Cloning {}".format(url))
    print("\n")

    if branch is None:
        R = pygit2.clone_repository(url, path, callbacks=MyRemoteCallbacks())
    else:
        branch = str(branch)
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
        url = remote.url
        remote.fetch(callbacks=MyRemoteCallbacks(), message='tags')
        print(remote.name, url)
        return remote
    else:
        return


def tags(repository=None):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    regex = re.compile('^refs/tags/')
    tag_list = [r.strip('refs/tags/') for r in repo.references if regex.match(r)]
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


def pull(repository=None):
    if repository is not None:
        repo = repository
    else:
        repo = pygit2.Repository(pygit2.discover_repository('./src'))
    if repo is None:
        raise RuntimeError('Unable to find valid git repository')

    remote_master_id = repo.lookup_reference('refs/remotes/origin/master').target
    repo.checkout_tree(repo.get(remote_master_id))
    master_ref = repo.lookup_reference('refs/heads/master')
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
        if args.branch is None:
            rep = clone(args.repo, args.clone)
        else:
            rep = clone(args.repo, args.clone, branch=args.branch)
