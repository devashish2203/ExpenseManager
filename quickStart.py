#!/usr/bin/python
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
from transaction import *
import calculations

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

def get_messageIds(service, Bank):
    """ Gets the text of all the messages matching the particular query"""
    request = service.users().messages().list(userId='me', q=Bank.query.value)
    response = request.execute()
    ids = []
    print(response)
    #Return is no messages found for query
    if "messages" not in response:
        return ids

    for obj in response['messages']:
        #print(obj['id'])
        print(obj)
        ids.append(obj['id'])
    while 'nextPageToken' in response:
        request = service.users().messages().list_next(request, response)
        response = request.execute()
        for obj in response['messages']:
            #print(obj['id'])
            print(obj)
            ids.append(obj['id'])

    print("There are "+str(len(ids))+" messages for "+Bank.name)
    return ids

def get_TransactionsFromIds(service, ids, Bank):
    transactions = []
    for mId in ids:
        msg_req = service.users().messages().get(userId='me', id=mId)
        msg_res = msg_req.execute()
        #print(msg_res['payload'])
        file_data = base64.urlsafe_b64decode(msg_res['payload']['body']['data'].encode('UTF-8'))
        parsed = parseHTMLforTransactionDetails(file_data, Bank.regexPattern.value)
        if parsed == None:
            continue
        trans = Transaction(parsed, Bank)
        print(trans)
        transactions.append(trans)
    
    return transactions

def parseHTMLforTransactionDetails(htmlBody, pattern):
    """ Returns a regex matcher object for the matched pattern"""
    pattern = re.compile(pattern)
    #print(htmlBody)
    result = re.search(pattern, htmlBody)
    
    if not result:
        print("No Pattern Match Found")
        #print(htmlBody)
        return None

    #print(result.groups())
    #print(result.group("merchant").strip()[:-1])
    return result


def main():
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    transactions = []
    for BankEnum in BankDetails:
        print("Serching for "+BankEnum.name)
        message_ids = get_messageIds(service, BankEnum.value)
        transactions+=get_TransactionsFromIds(service, message_ids, BankEnum.value)
        print(len(transactions))

        bucket = calculations.getTotalSpendsByMonth(transactions)
        print(bucket)
        print("Total Spends: "+str(calculations.getTotalSpends(transactions)))
    #message_list = get_messageText(service, 'airtel')
    #pprint(message_list)

if __name__ == '__main__':
    main()