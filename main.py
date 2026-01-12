import asyncio
from fastapi import FastAPI
from routers.auth import router as router_auth
from routers.webhooker import router as router_webhooker

import uvicorn

import config

import gmail_webhook


import os



async def main():        
    for name, url_and_query in config.r.hgetall("started_webhooks").items():
        asyncio.create_task(gmail_webhook.init(name, *url_and_query.values()))
    
    
    app = FastAPI()
    
    app.include_router(router_auth, prefix="/auth", tags=["Auth"])
    app.include_router(router_webhooker, prefix="/webhooker", tags=["Mfest Wholesale Webhooker"])
    
    app_config = uvicorn.Config(
        host="0.0.0.0",
        app = app,
        port = 8080
    )
    server = uvicorn.Server(app_config)
    await server.serve()
    


if __name__ == "__main__":
    if not os.path.exists("tokens"):
        os.makedirs("tokens")
    asyncio.run(main())