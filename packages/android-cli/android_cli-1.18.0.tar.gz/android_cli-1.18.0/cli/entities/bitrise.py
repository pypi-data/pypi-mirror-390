import copy
import json
import sys
import threading
import time

import requests

from cli.entities.setting import Settings
from cli.utils.singleton import singleton


def show_loading_spinner(is_loading, message="Loading, please wait ..."):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    while is_loading.is_set():
        for char in spinner:
            sys.stdout.write(f'\r{char} {message}')
            time.sleep(0.1)
            sys.stdout.flush()
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


@singleton
class Bitrise:

    def __init__(self, settings=Settings()):
        self.credentials = settings.get_bitrise_credentials()
        self.data = {
            "base_branch": "main",
            "version_code": "544",
            "version_name": "1.24.0",
            "release_notes": "release_notes"
        }

        self.bitrise_config = {
            "hook_info": {
                "type": "bitrise",
                "build_trigger_token": self.credentials["test"]["build_trigger_token"]
            },
            "build_params": {
                "branch": self.data['base_branch'],
                "workflow_id": "deploy-feature-release",
                "environments": [
                    {
                        "mapped_to": "MY_VERSION_NAME",
                        "value": self.data['version_name'],
                        "is_expand": True
                    },
                    {
                        "mapped_to": "MY_VERSION_CODE",
                        "value": self.data['version_code'],
                        "is_expand": True
                    },
                    {
                        "mapped_to": "MY_RELEASE_NOTES",
                        "value": self.data['release_notes'],
                        "is_expand": True
                    }
                ]
            },
            "triggered_by": "curl"
        }

        self.bitrise_release = copy.deepcopy(self.bitrise_config)

    @staticmethod
    def get_release_config(self, branch, release_notes, env):
        release_copy = copy.deepcopy(self.bitrise_release)
        release_copy["hook_info"]["build_trigger_token"] = self.credentials[env]["build_trigger_token"]
        release_copy["build_params"]["workflow_id"] = "deploy-release"
        release_copy["build_params"]["branch"] = branch
        release_copy['build_params']['environments'] = self.bitrise_config['build_params']['environments'][2:]
        release_copy["build_params"]["environments"][0]["value"] = release_notes

        return release_copy

    @staticmethod
    def get_feature_branch_config(self, branch, release_notes, version_name, version_code, env):
        feature_branch_copy = copy.deepcopy(self.bitrise_config)
        feature_branch_copy["hook_info"]["build_trigger_token"] = self.credentials[env]["build_trigger_token"]
        feature_branch_copy["build_params"]["branch"] = branch
        feature_branch_copy["build_params"]["environments"][0]["value"] = version_name
        feature_branch_copy["build_params"]["environments"][1]["value"] = version_code
        feature_branch_copy["build_params"]["environments"][2]["value"] = release_notes
        return feature_branch_copy

    def generate_release_curl(self, branch, release_notes, env):
        json_data = json.dumps(self.get_release_config(self, branch, release_notes, env))
        curl_command = f"curl https://app.bitrise.io/app/{self.credentials[env]['curl_url_id']}/build/start" \
                       f".json -L --data '{json_data}' "
        return curl_command

    def generate_feature_branch_curl(self, branch, release_notes, version_name, version_code, env):
        json_data = json.dumps(
            self.get_feature_branch_config(self, branch, release_notes, version_name, version_code, env))
        curl_command = f"curl https://app.bitrise.io/app/{self.credentials[env]['curl_url_id']}/build/start" \
                       f".json -L --data '{json_data}' "
        return curl_command

    def execute_release_curl(self, branch, release_notes, env):
        url = f"https://app.bitrise.io/app/{self.credentials[env]['curl_url_id']}/build/start"
        json_data = json.dumps(self.get_release_config(self, branch, release_notes, env))

        headers = {
            "Content-Type": "application/json"
        }

        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Please, wait ..."))
        spinner_thread.start()

        try:
            response = requests.post(url, headers=headers, data=json_data)
        finally:
            is_loading.clear()
            spinner_thread.join()

        print(response.status_code)
        print(response.text)

    def execute_feature_branch_curl(self, branch, release_notes, version_name, version_code, env):
        url = f"https://app.bitrise.io/app/{self.credentials[env]['curl_url_id']}/build/start"
        json_data = json.dumps(
            self.get_feature_branch_config(self, branch, release_notes, version_name, version_code, env))

        headers = {
            "Content-Type": "application/json"
        }

        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Please, wait ..."))
        spinner_thread.start()

        try:
            response = requests.post(url, headers=headers, data=json_data)
        finally:
            is_loading.clear()
            spinner_thread.join()

        print(response.status_code)
        print(response.text)
