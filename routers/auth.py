from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

import config

import os

from google.auth.transport.requests import Request as GmailAPIRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow




router = APIRouter()


@router.post('/{name}')
async def auth(
    name: str,
    api_key: str = Header()
):
    if api_key != config.API_KEY:
        return JSONResponse(
            content = {
                "success": False,
                "description": "Wrong api-key"
            },
            status_code = 401
        )
        
        
    token = None
    if os.path.exists(f"tokens/{name}.json"):
        token = Credentials.from_authorized_user_file(f"tokens/{name}.json", ["https://www.googleapis.com/auth/gmail.readonly"])

    if token != None and token.expired and token.refresh_token:
        token.refresh(GmailAPIRequest())
    elif token==None or not token.valid:
        flow = Flow.from_client_secrets_file(
            "credentials.json",
            ["https://www.googleapis.com/auth/gmail.readonly"],
            redirect_uri = f"{config.THIS_URL}/auth/response",
            state=name
        )
        
        authorization_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
        return JSONResponse(
            content = {
                "success": True,
                "auth_url": authorization_url,
                "description": "To continue login using auth url"
            }
        )
        
        
    return JSONResponse(
        content = {
            "success": True,
            "description": "Token already created"
        }
    )
    


@router.get('/response')
async def auth_response(
    state: str,
    code: str,
    scope: str
):
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        ["https://www.googleapis.com/auth/gmail.readonly"],
        redirect_uri = f"{config.THIS_URL}/auth/response",
        state = state
    )
    
    
    token = flow.fetch_token(code=code)
        
    with open(f"tokens/{state}.json", "w") as f:
        f.write(flow.credentials.to_json())
    
    return JSONResponse(
        content = {
            "success": True,
            "description": "Your token was created successfully.\nNow you can use gmail api"
        }
    )