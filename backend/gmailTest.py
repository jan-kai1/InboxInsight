import os.path
from regexes import replaceLinks
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  query = "is: unread"
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "creds/client_secret.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", q = query).execute()
    messages = results.get("messages", [])

    if not messages:
      print("No labels found.")
      return
    count = 0
    for msg in messages:
        if count > 5:
            break
        detailed = service.users().messages().get(userId = "me", id = msg['id']).execute()
        print(replaceLinks(detailed['snippet']))
        # print(replaceLinks(detailed['payload']['headers']))
        # print((detailed['payload']['body']))
        parts = detailed['payload'].get('parts', [])
        
        for part in parts:
          
          mimeType = part.get('mimeType')
          if mimeType == 'text/plain':
            bodyData = part['body'].get('data')
            if bodyData:
                raw_data = base64.urlsafe_b64decode(bodyData.encode('UTF-8'))
                text_content = raw_data.decode('UTF-8')
                print(replaceLinks(text_content))
            else:
              print("notext")

        print('---')
        count +=1

    #   print(msg["snippet"])
        
    #   print(msg['payload']['body'])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()