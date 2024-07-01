from simplegmail import Gmail
from simplegmail.query import construct_query
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

client_secret_path = 'creds/client_secret.json'
token_path = 'creds/gmail_token.json'
# fullPath = "D:/Private/emailProj2/backend/creds/client_secret.json"
# gmail = Gmail("/creds/client_secret.json", "/creds/gmail_token.json")
# print(os.path.exists(client_secret_path))
# print(os.path.exists(fullPath))
gmail = Gmail(client_secret_file =client_secret_path, creds_file=token_path)
query_params = {
    "newer_than" : (4 , "day"),
    # "unread" : True,
    "in" : "inbox"

}

#returns plain messages objects
def plainEmails():
    messages = gmail.get_messages(query = construct_query(query_params))
    data = []
    for msg in messages:
        msgObj = { "subject": msg.subject, "date" : msg.date, "sender" : msg.sender, "snippet" : msg.snippet, "plain" : msg.plain}
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