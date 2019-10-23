import pickle
import os.path
import time
import logging

from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors  # TODO


log = logging.getLogger('gmailsync')


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class MessageFetcher:

    def __init__(self):
        self.messages = []

    def fetch_message(self, request_id, response, exception):
        if exception is not None:
            log.error('Error fetching a message: server exception. request_id: %s, response: %s, exception: %s',
                request_id, response, exception)
            return

        if 'raw' not in response:
            log.error('Error fetching a message: malformed response. request_id: %s, response: %s',
                request_id, response)
            return

        self.messages.append(response)


class Client:

    def __init__(self, token_path):
        creds = self._authenticate(token_path)
        self.service = build('gmail', 'v1', credentials=creds)

    def _authenticate(self, token_path):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def labels(self):
        response = self.service.users().labels().list(userId='me').execute()
        return response.get('labels', [])

    def list(self, since=None):
        # TODO: test discard chats
        query = '!in:chat'
        if since:
            query += ' after:{}'.format(since)

        response = self.service.users().messages().list(userId='me', q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        else:
            log.error('Error fetching listing messages: malformed response. response: %s, page_token: %s',
                response, None)

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(userId='me', q=query,
                pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
            else:
                log.error('Error fetching listing messages: malformed response. response: %s, page_token: %s',
                response, page_token)

        return messages

    def get(self, message_id):
        response = self.service.users().messages().get(userId='me', id=message_id,
            format='raw').execute()
        return response.get('raw')

    # def fetch(self, callback, since=None):
    #     msg_list = self.list(since)

    #     # Sending batches larger than 50 requests is not recommended.
    #     # https://developers.google.com/gmail/api/v1/reference/quota
    #     for chunk in chunked(msg_list, 50):
    #         batch = BatchHttpRequest()
    #         for msg_desc in chunk:
    #             batch.add(self.service.users().messages().get(userId='me', id=msg_desc['id'],
    #                 format='raw'), callback=callback)
    #         batch.execute()

    #         # Safe path to avoid quota limits: 250 quota units per user per second
    #         # https://developers.google.com/gmail/api/v1/reference/quota
    #         time.sleep(1)

    def fetch(self, msg_ids):
        fetcher = MessageFetcher()

        batch = BatchHttpRequest()
        for msg_desc in msg_ids:
            batch.add(self.service.users().messages().get(userId='me', id=msg_desc['id'],
                format='raw'), callback=fetcher.fetch_message)
        batch.execute()

        return fetcher.messages
