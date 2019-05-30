#!/usr/bin/python
from __future__ import print_function
import httplib2
import os
import re
import pickle

from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pprint import pprint
import base64
from transaction import *
import calculations
import argparse

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
    credentials_path_pickle = os.path.join(credential_dir,
                                   'gmail-python-quickstart.pickle')
    
    credentials = None
    if os.path.exists(credentials_path_pickle):
        with open(credentials_path_pickle, "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server()

        with open(credentials_path_pickle, 'wb') as token:
            pickle.dump(credentials, token)
        


    
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
    count = 500
    for mId in ids:
        count = count - 1
        if count == 0:
            break
        msg_req = service.users().messages().get(userId='me', id=mId)
        msg_res = msg_req.execute()
        #print(msg_res['payload'])
        file_data = base64.urlsafe_b64decode(msg_res['payload']['body']['data']).decode()
        parsed = parseHTMLforTransactionDetails(file_data, Bank.regexPattern.value)
        if parsed == None:
            continue
        trans = Transaction(parsed, Bank)
        print(count, trans)
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
    service = discovery.build('gmail', 'v1', credentials=credentials)

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
