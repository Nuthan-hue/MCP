from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes

app = FastAPI()

# If modifying scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class EmailRequest(BaseModel):
    filter: str = "unread"
    count: int = 1

class Email(BaseModel):
    subject: str
    body: str

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

@app.post("/read_emails", response_model=List[Email])
def read_emails(req: EmailRequest):
    service = get_service()

    # Fetch unread messages
    results = service.users().messages().list(userId="me", maxResults=req.count).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = full_msg["payload"]
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        
        parts = payload.get("parts", [])
        body = ""
        for part in parts:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        
        emails.append({"subject": subject, "body": body})

    return emails

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
