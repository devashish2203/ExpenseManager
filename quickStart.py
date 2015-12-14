from __future__ import print_function
import httplib2
import os
import re

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from pprint import pprint
import base64
from enum import Enum

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ExpenseManager'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_messageText(service, query=''):
    """ Gets the text of all the messages matching the particular query"""
    request = service.users().messages().list(userId='me', q=query)
    response = request.execute()
    pprint(response)
    ids = []
    for obj in response['messages']:
        #print(obj['id'])
        ids.append(obj['id'])
    fetchNext = 'nextPageToken' in response
    while fetchNext:
        request = service.users().messages().list_next(request, response)
        response = request.execute()
        pprint(response)
        for obj in response['messages']:
            #print(obj['id'])
            ids.append(obj['id'])
        fetchNext = 'nextPageToken' in response

    print("There are "+str(len(ids))+" messages")
    message_text = []

    amount = []
    ccNo = []
    date = []
    merchant = []
    for mId in ids:
        msg_req = service.users().messages().get(userId='me', id=mId)
        msg_res = msg_req.execute()
        file_data = base64.urlsafe_b64decode(msg_res['payload']['body']['data'].encode('UTF-8'))
        parsed = parseHTMLforTransactionDetails(file_data)
        amount.append(parsed.group("amount"))
        ccNo.append(parsed.group("ccNo"))
        date.append(parsed.group("date"))
        merchant.append(parsed.group("merchant"))

    print(amount)
    return amount

def parseHTMLforTransactionDetails(htmlBody):
    """ Returns a regex matcher object for the matched pattern"""
    pattern = re.compile(Pattern.CitiBank.value)
    #print(htmlBody)
    result = re.search(pattern, htmlBody)
    if result:
        print(result.groups())
    else:
        print(htmlBody)
    #print(result.groups())
    #print(result.group("merchant").strip()[:-1])
    return result



def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    message_list = get_messageText(service, 'from:citialert.india@citicorp.com subject:Transaction Confirmation')
    #message_list = get_messageText(service, 'airtel')
    #pprint(message_list)


class Pattern(Enum):
    CitiBank = "Rs (?P<amount>[\d,]+\.\d{2}).*(?P<ccNo>\d{4}X{8}\d{4}) on (?P<date>.*) at (?P<merchant>.*)"
if __name__ == '__main__':
    main()