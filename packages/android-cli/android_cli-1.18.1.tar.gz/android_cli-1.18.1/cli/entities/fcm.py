import json
import os

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from cli.utils.singleton import singleton


@singleton
class FCM:
    def __init__(self):
        path = os.getcwd()
        self.account_file = f"{path}/app/src/tst/assets/service-account.json"
        self.project_id = "astropaycarduitest"
        self.credentials = service_account.Credentials.from_service_account_file(
            self.account_file,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        self.credentials.refresh(Request())
        auth_token = self.credentials.token
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json; UTF-8',
        }

    def send_push(self, device_token, title, body, deeplink):
        if not self.credentials.valid:
            self.credentials.refresh(Request())

        message = {
            'message': {
                'notification': {
                    'title': title,
                    'body': body
                },
                'data': {
                    # 'action': "TRUSTED_DEVICE",
                    # 'title': title,
                    # 'body': body,
                    'deeplink': deeplink
                },
                'token': device_token,
                'android': {
                    'priority': 'high'
                },
                'apns': {
                    'headers': {
                        'apns-priority': '5'
                    },
                    'payload': {
                        'aps': {
                            'content-available': 1
                        }
                    }
                }
            }
        }
        print(message)
        url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        response = requests.post(url, headers=self.headers, json=message)
        print('Status Code:', response.status_code)
        print('Response:', response.json())
        return ""

    def send_silent_push(self, device_token, action):
        if not self.credentials.valid:
            self.credentials.refresh(Request())

        message = {
            'message': {
                'token': device_token,
                'android': {
                    'priority': 'normal'
                },
                'apns': {
                    'headers': {
                        'apns-priority': '5'
                    },
                    'payload': {
                        'aps': {
                            'content-available': 1
                        }
                    }
                },
                'data': {
                    'action': action
                }
            }
        }
        print(message)
        url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        response = requests.post(url, headers=self.headers, json=message)
        print('Status Code:', response.status_code)
        print('Response:', response.json())
        return ""
