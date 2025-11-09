import os
import subprocess
from cli.utils.shell import Shell
from cli.utils.singleton import singleton


@singleton
class Git:

    @staticmethod
    def get_branches():
        if os.path.isdir('.git'):
            try:
                Shell().run(['git', 'fetch', '-p'], show_loading=True)
                branches_output = subprocess.check_output(['git', 'branch', '-r'],
                                                          stderr=subprocess.STDOUT).decode().strip()
                branches = [branch.strip() for branch in branches_output.split("\n") if branch.strip()]
                branches = [branch for branch in branches if not branch.startswith('origin/HEAD')]
                branches = [branch.replace('origin/', '') for branch in branches if not branch.startswith('origin/HEAD')]
                return branches
            except subprocess.CalledProcessError:
                return False
        else:
            return False

    @staticmethod
    def has_changes():
        has_changes = os.popen('git status --porcelain').read().strip() != ""
        if has_changes:
            return True
        else:
            return False

    @staticmethod
    def get_current_branch():
        try:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                             stderr=subprocess.STDOUT).decode().strip()
            return branch
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_repository_name(showError=True):
        try:
            result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], capture_output=True, text=True,
                                    check=True)
            repo_url = result.stdout.strip()
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_name = repo_name.split('@')[1]

            return repo_name
        except subprocess.CalledProcessError:
            if showError:
                print("Error al obtener la URL del repositorio remoto.")
            return None

    @staticmethod
    def get_last_commit(full=False):
        try:
            commit = subprocess.check_output(['git', 'log', '-1', '--pretty=%B'], stderr=subprocess.STDOUT).decode().strip()
            if full:
                return commit
            else:
                commit = commit.replace('\n', '+')
                if len(commit) > 70:
                    commit = commit[:67] + '...'
                return commit
        except subprocess.CalledProcessError:
            return False
