from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

def main():
    SERVICE_ACCOUNT_FILE = 'service_cred.json'

    def create_cloudidentity_service():
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/cloud-identity.devices'])
        delegated_credentials = credentials.with_subject(<USERNAME>)

        service_name = 'cloudidentity'
        api_version = 'v1'
        service = googleapiclient.discovery.build(
            service_name,
            api_version,
            credentials=delegated_credentials)

        return service

    def create_directory_service():
        SCOPES=['https://www.googleapis.com/auth/admin.directory.user']

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service_name = 'admin'
        api_version = 'directory_v1'
        service = googleapiclient.discovery.build(
            service_name,
            api_version,
            credentials=creds)

        return service

    cloudidentity = create_cloudidentity_service()
    devices = cloudidentity.devices().list(pageSize=1000).execute()

    directory = create_directory_service()

    for device in devices.get('devices'):
        users = cloudidentity.devices().deviceUsers().list(parent=device["name"]).execute()
        for user in users.get('deviceUsers'):
            dir_users = directory.users().get(userKey=user['userEmail']).execute()
            print(f'{dir_users["name"]["givenName"]}\'s {device["model"] if "model" in device else "device"}')


if __name__ == '__main__':
    main()
