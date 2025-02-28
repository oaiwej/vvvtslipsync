import websockets
import json
import sys
import asyncio
import aiofiles
import os

class VTSClient:
    def __init__(self, plugin_name, plugin_developer, ws_url):
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.ws_url = ws_url
        self.websocket_session = None
        self.authenticated_token = None

    async def connect(self):
        self.websocket_session = await websockets.connect(self.ws_url)
        token = await self.load_token()
        if token is None:
            token = await self.request_token()
        
        authenticated = await self.authenticate(token)
        if not authenticated:
            print("VTubeStudio authentication failed", file=sys.stderr)
            await self.websocket_session.close()
            await self.shutdown_server()
            sys.exit(1)
        else:
            print("VTubeStudio authentication successful")
            
        self.authenticated_token = token
        await self.save_token()

    async def disconnect(self):
        if self.websocket_session:
            await self.websocket_session.close()

    async def request_token(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "TokenRequestID",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer
            }
        }
        await self.websocket_session.send(json.dumps(request))
        response = await self.websocket_session.recv()
        return json.loads(response)["data"]["authenticationToken"]

    async def authenticate(self, token):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "AuthenticationRequestID",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "authenticationToken": token
            }
        }
        await self.websocket_session.send(json.dumps(request))
        response = await self.websocket_session.recv()
        return json.loads(response)["data"]["authenticated"]

    async def shutdown_server(self):
        loop = asyncio.get_event_loop()
        for task in asyncio.all_tasks(loop):
            task.cancel()

    async def save_token(self):
        async with aiofiles.open("vts_token.txt", "w") as f:
            await f.write(self.authenticated_token)

    async def load_token(self) -> str | None:
        if not os.path.exists("vts_token.txt"):
            return None
        
        async with aiofiles.open("vts_token.txt", "r") as f:
            authenticated_token = await f.read()

        return authenticated_token
