import logging
import asyncio
from fastapi import FastAPI, Request, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from guacamole.client import GuacamoleClient
from guacamole.instruction import Instruction

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

WEBSOCKETS = {}


@app.get("/", response_class=HTMLResponse)
def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def guacd_to_client(websocket: WebSocket, client: GuacamoleClient):
    while True:
        instruction = await client.read()
        if instruction.error:
            logging.error(
                f"{instruction.short_description}-{instruction.description}"
            )
        await websocket.send_text(str(instruction))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    await websocket.accept(subprotocol="guacamole")
    client = GuacamoleClient(
        "74.207.234.105",
        4822,
        {
            "protocol": "vnc",
            "size": [1024, 768, 96],
            "audio": [],
            "video": [],
            "image": [],
            "args": {
                "hostname": "2.tcp.ngrok.io",
                "port": 10261,
                "username": "Remote",
                "password": "",
            },
        },
        debug=True,
    )

    await client.connect()
    await client.handshake()

    task = asyncio.get_event_loop().create_task(guacd_to_client(websocket, client))

    try:
        while True:
            data = await websocket.receive_text()
            instruction = Instruction.from_string(data)
            await client.send(str(instruction))
    except WebSocketDisconnect:
        task.cancel()
        await client.close()
