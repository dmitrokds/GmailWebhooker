import os

import config

from google.auth.transport.requests import Request as GmailAPIRequest
from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build
import bs4
import base64

import asyncio
import aiohttp


async def init(token_name: str, url: str, query: str):
    token = None
    if os.path.exists(f"tokens/{token_name}.json"):
        token = Credentials.from_authorized_user_file(f"tokens/{token_name}.json", ["https://www.googleapis.com/auth/gmail.readonly"])

    if token != None and token.expired and token.refresh_token:
        token.refresh(GmailAPIRequest())
    
    if token==None or not token.valid:
        print("token is not valid")
        return
    
    
    service = build("gmail", "v1", credentials=token)

    while True:
        filtered_msgs = service.users().messages().list(userId="me", q=query).execute()
        print(f"LEN of messages: {filtered_msgs}")
        
        for msg_id in filtered_msgs["messages"]:
            if msg_id['id'] == config.r.hget("last_msg_id", token_name):
                break
            msg = service.users().messages().get(userId="me", id=msg_id["id"]).execute()
            
            snippet = msg["snippet"]
            sender = next((header["value"] for header in msg["payload"]["headers"] if header["name"] == "From"), None)
            receiver = next((header["value"] for header in msg["payload"]["headers"] if header["name"] == "To"), None)
            subject = next((header["value"] for header in msg["payload"]["headers"] if header["name"] == "Subject"), None)
            body = base64.urlsafe_b64decode(
                msg["payload"]["body"]["data"].encode("ASCII")
            ).decode("utf-8")
            
            async with aiohttp.ClientSession() as sess:
                async with sess.post(url, json={
                    "snippet": snippet,
                    "subject": subject,
                    "sender": sender,
                    "receiver": receiver,
                    "body": body
                }, headers={"accept": "application/json"}):
                    pass

        
        
        if len(filtered_msgs["messages"]) > 0:
            config.r.hset("last_msg_id", token_name, filtered_msgs["messages"][0]["id"])
            
            
            
        await asyncio.sleep(60)