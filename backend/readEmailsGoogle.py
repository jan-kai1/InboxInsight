from regexes import replaceLinks
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup
from regexes import replaceLinks
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
load_dotenv("gemini.env")
# API_KEY = gemini.env.ENV_API_KEY
API_KEY = os.getenv('ENV_API_KEY')
genai.configure(api_key = API_KEY )
model = genai.GenerativeModel("gemini-1.5-flash")

SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.readonly"]
DEV_GMAIL_TOKEN_PATH = "creds/gmail_token.json"
DEV_CLIENT_SECRET_PATH = "creds/client_secret.json"

def processMessage(msg, service):
        #currently just gets text from the msges
        fullMessage  = service.users().messages().get(userId = "me", id = msg['id']).execute()
        snippet = replaceLinks(fullMessage['snippet'])
        payload = fullMessage['payload']
        headers = payload.get('headers', [])
        # misc stores the miscellenous data, can add more if needed
        misc = {"From" : None , "Subject" : None, "Date" : None}
        for header in headers:
            if header['name'] in misc:
                misc[header['name']] = header['value']

        plain = None
        parts = payload.get('parts', [])
        payloadBody = payload.get("body").get("data")
        # filterBody = base64.urlsafe_b64decode(payloadBody.encode("UTF-8"))
        # filterBody = replaceLinks(filterBody)
        raw_data = None
        for part in parts:
            mimeType = part.get('mimeType')
            if mimeType == 'text.plain' or mimeType == "text/html":
                bodyData = part['body'].get('data')
                if bodyData:
                    raw_data = base64.urlsafe_b64decode(bodyData).decode("utf-8")
                    
                    soup  = BeautifulSoup(raw_data, 'lxml')
                    # plain = replaceLinks(text_content)
                    text = soup.get_text()
                    lines = [line.strip() for line in text.splitlines()]
                    plain = '\n'.join(line for line in lines if line)
                    plain = replaceLinks(plain)
        # rawText = fullMessage['raw']
        # raw_data = base64.urlsafe_b64decode(rawText.encode('UTF-8'))
        # trialRaw = replaceLinks(raw_data)
        return { "subject" : misc['Subject'], 
                "date" : misc['Date'], 
                "sender" : misc['From'], 
                "snippet" : snippet, 
                "plain" : plain,
                "raw" : raw_data }

def authenticate(gmail_token_path, client_secret_path):
    creds = None
    if os.path.exists(gmail_token_path):
        creds = Credentials.from_authorized_user_file(gmail_token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # modify this to temporary file 
        with open(gmail_token_path, "w") as token:
            token.write(creds.to_json())
    # print("authenticated")
    return creds

# must return email as an obj {subject, date, sender, snippet, plain}
def plainEmails(gmail_token_path = DEV_GMAIL_TOKEN_PATH, client_secret_path = DEV_CLIENT_SECRET_PATH):
    def processMessage(msg):
        #currently just gets text from the msges
        fullMessage  = service.users().messages().get(userId = "me", id = msg['id'], format = "RAW").execute()
        snippet = replaceLinks(fullMessage['snippet'])

        payload = fullMessage['payload']
        headers = payload.get('headers', [])
        # misc stores the miscellenous data, can add more if needed
        misc = {"From" : None , "Subject" : None, "Date" : None}
        for header in headers:
            if header['name'] in misc:
                misc[header['name']] = header['value']

        plain = None
        parts = payload.get('parts', [])
        for part in parts:
            mimeType = part.get('mimeType')
            if mimeType == 'text.plain':
                bodyData = part['body'].get('data')
                if bodyData:
                    raw_data = base64.urlsafe_b64decode(bodyData.encode('UTF-8'))
                    text_content = raw_data.decode('UTF-8')
                    plain = replaceLinks(text_content)
        rawText = fullMessage["raw"]
        testRaw = replaceLinks(rawText)
        return { "subject" : misc['Subject'], "date" : misc['Date'], "sender" : misc['From'], "snippet" : snippet, "plain" : plain, "raw" : testRaw}

        



    
    # modify this for changing query
    # time period, yy/mm/dd before: after"
    #older_than: newer_than: takes in y m or d
    #https://support.google.com/mail/answer/7190
    query = "is:unread newer_than:3d"
    try:
        creds = authenticate(gmail_token_path, client_secret_path)
        service  = build("gmail", "v1", credentials = creds)
        # returns a list of messages with msg['id']
        #have to query again to get the actual text (processed in processMessage)
        results = service.users().messages().list(userId="me", q = query).execute()
        # print(results)
        messages = results.get("messages" , [])
        data = []
        # print("going thru msg")
        for msg in messages:
            msgObj = processMessage(msg)
            # print(msgObj)
            data.append(msgObj)
        return data
    
    except HttpError as error:
        print(f"an error occured: {error}")

def getEmails(authToken): #uses auth token from authorization callback
    
    
    
    if not authToken:
        return {'error' : 'user not logged in'} , 401
    else:
        # modify this for changing query
        # time period, yy/mm/dd before: after"
        #older_than: newer_than: takes in y m or d
        #https://support.google.com/mail/answer/7190
        query = "is:unread newer_than:3d"

        service  = build("gmail", "v1", credentials = Credentials.from_authorized_user_info(authToken))
        # returns a list of messages with msg['id']
        #have to query again to get the actual text (processed in processMessage)
        results = service.users().messages().list(userId="me", q = query).execute()
        # print(results)
        messages = results.get("messages" , [])
        data = []
        # print("going thru msg")
        for msg in messages:
            msgObj = processMessage(msg,  service)
            # print(msgObj)
            data.append(msgObj)
        return data



def summarizeEmail(text):
    maxTries = 5
    attempts = 0
    def trySummarize(text) :
        nonlocal attempts
        try:
            filtered = replaceLinks(text)
            # print(filtered)
            summary = model.generate_content(f"Summarize this: {filtered}").text
        
            if summary == None:
                attempts += 1
                return trySummarize(text)
            return summary

        except Exception as e:
            if attempts < maxTries:

                attempts += 1
                time.sleep(2)
                trySummarize(text)
            else:
                print("max tries reached")
                raise e
    return trySummarize(text)
    


def main():
    print(plainEmails())
if __name__ == "__main__":
    main()