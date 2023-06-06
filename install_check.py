# install_check.py

import sys
import subprocess
import pkg_resources  # https://jmchilton-galaxy.readthedocs.io/en/latest/lib/pkg_resources.html
# from pkg_resources import DistributionNotFound, VersionConflict
from packaging import version
import os
import git_tools

from Settings import Settings
SETTINGS = Settings(os.getcwd())
SETTINGS.file = os.path.normpath(os.path.join(os.getcwd(), "install_settings.json"))
SETTINGS.read_settings()


class PackageChecker:
    def __init__(self, file='./src/requirements.txt'):
        self.file = file
        
        # dependencies can be any iterable with strings, 
        # e.g. file line-by-line iterator
        requirements = open(self.file, 'r')
        dependencies = [i for i in requirements.readlines()]
        dependencies = [i for i in dependencies if '#' not in i]
        self.dependencies = [i.strip('\n') for i in dependencies]
    
    def check(self):
        # here, if a dependency is not met, a DistributionNotFound or VersionConflict
        # exception is thrown.
        version_errors = []
        missing_errors = []
        for d in self.dependencies:
            try:
                pkg_resources.require([d])

            except pkg_resources.VersionConflict as e:
                # print('pkg_resources.VersionConflict')
                # print(e)
                
                #  d = required package string from requirements.txt
                #  e.dist = installed
                #  e.req = required
                version_errors.append({'package': d.split('=')[0],
                                       'installed': e.dist,
                                       'required': d})

            except pkg_resources.DistributionNotFound as e:
                # print('pkg_resources.DistributionNotFound')
                # print(e)
                missing_errors.append({'package': d.split('=')[0],
                                       'installed': 'n/a',
                                       'required': d})
        bad_depends = {
            'version': version_errors,
            'missing': missing_errors
        }
        return bad_depends
    
    def fix(self):
        bad_pkgs = self.check()
        bad_pkgs = bad_pkgs['version'] + bad_pkgs['missing']
        for p in bad_pkgs:
            # print(p, type(p))
            install(p['required'])

            
def install(package):
    r = subprocess.run([sys.executable, "-m", "pip", "install", package])
    r.check_returncode()


def print_table(table):
    col_width = [max([len(str(x)) for x in col])+2 for col in zip(*table)]
    for line in table:
        print("| " + " | ".join("{:{}}".format(str(x), col_width[i]) for i, x in enumerate(line)) + " |")


def newest_version(available_versions: list):
    latest = available_versions[0]
    prev_ver = '0'
    for v in available_versions:
        if version.parse(v.split('-')[0]) > version.parse(prev_ver.split('-')[0]):
            latest = v
        prev_ver = v
    return latest


def git_update():
    # git updates
    git_target = SETTINGS.git['url']

    print('Fetching Updates from GitHub: https://[key]@github.com{}'.format(git_target))
    git_tools.fetch()

    proj_versions = git_tools.tags()
    current_version = git_tools.current_version()
    print('\nCurrent version:', current_version, '\nAvailable versions:', proj_versions)
    newer_versions = []
    for v in proj_versions:
        if version.parse(v.split('-')[0]) > version.parse(current_version.split('-')[0]):
            newer_versions.append(v)
    if len(newer_versions) != 0:
        print('    Newer versions:', newer_versions)
        # Ask user if they want to proceed with git project updates
        ans = input('Update to {}? (Y/N): '.format(newest_version(newer_versions)))
        if ans.lower().startswith('y'):
            print('\nUpdating!')
            # git_tools.pull(base, tag=newest_version(newer_versions)) TODO
        else:
            print('OVERWRITES CURRENT INSTALL')
            ans = input('OK, enter valid version number to install (or None to skip update):')
            if ans in proj_versions:
                print('\nInstalling {}!'.format(ans))
                git_tools.install_version(ans)
            else:
                print('Cancelling!')
    else:
        print('You are on the latest version')


def pkgs_update():
    # Environment/Package updates
    c = PackageChecker()
    b = c.check()
    n_version_errs = len(b['version'])
    n_missing_errs = len(b['missing'])

    if n_version_errs == n_missing_errs == 0:
        print('Environment Verified GOOD')
    else:
        print('\n', 'Package version errors:')
        all_data = [['Package', 'Installed', 'Required']]
        for i in b['version']:
            all_data.append([i['package'], i['installed'], i['required']])
        print_table(all_data)

        print('\n', 'Packages missing:')
        all_data = [['Package', 'Installed', 'Required']]
        for i in b['missing']:
            all_data.append([i['package'], i['installed'], i['required']])
        print_table(all_data)

        # Ask user if they want to proceed with package updates
        ans = input('Proceed with package updates? (Y/N): ')
        if ans.lower().startswith('y'):
            print('\nUpdating!')
            c.fix()
        else:
            print('Cancelling Update! Proceeding with Errors')
        

if __name__ == '__main__':
    git_update()
    pkgs_update()

    # Install
    # Prereqs
    #   embedded python.exe at dist/bin
    #       needs pip from get-pip.py
    #   /dist/bin/python.exe -m pip install packaging
    # setup git
    # - git init
    # - git pull {url} main

