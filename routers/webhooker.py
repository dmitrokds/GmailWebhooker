from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

import config

import os

from google.auth.transport.requests import Request as GmailAPIRequest
from google.oauth2.credentials import Credentials

import asyncio

import gmail_webhook




router = APIRouter()


@router.post('/start/{name}')
async def start(
    name: str,
    url: str,
    query: str,
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
        
    if config.r.hexists("started_webhooks", name):
        return JSONResponse(
            content = {
                "success": True,
                "description": "Already started webhook"
            },
            status_code = 204
        )
        
        
    token = None
    if os.path.exists(f"tokens/{name}.json"):
        token = Credentials.from_authorized_user_file(f"tokens/{name}.json", ["https://www.googleapis.com/auth/gmail.readonly"])

    if token != None and token.expired and token.refresh_token:
        token.refresh(GmailAPIRequest())
    elif token==None or not token.valid:
        return JSONResponse(
            content = {
                "success": False,
                "description": "Token is not existed or expired"
            },
            status_code=400
        )
        
        
    asyncio.create_task(gmail_webhook.init(name, url, query))
    config.r.hset("started_webhooks", name, {"url": url, "query": query})
        
        
    return JSONResponse(
        content = {
            "success": True,
            "description": "Webhook is started"
        }
    )
    


@router.post('/stop/{name}')
async def stop(
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
        
    if not config.r.hexists("started_webhooks", name):
        return JSONResponse(
            content = {
                "success": True,
                "description": "Webhook is not existed"
            },
            status_code = 204
        )
        
    
    config.r.hdel("started_webhooks", name)
        
        
    return JSONResponse(
        content = {
            "success": True,
            "description": "Webhook is stopped"
        }
    )



@router.get('/status/{name}')
async def get_status(
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
        
        
        
    return JSONResponse(
        content = {
            "success": True,
            "is_started": config.r.hexists("started_webhooks", name)
        }
    )