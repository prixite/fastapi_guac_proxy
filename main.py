import asyncio
from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
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


async def socket_to_client(websocket: WebSocket, client: GuacamoleClient):
    await client.connect()
    await client.handshake()
    while True:
        instruction = await client.read()
        if instruction.error:
            print("ERROR", instruction.short_description, instruction.description)
        await websocket.send_text(str(instruction))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    await websocket.accept(subprotocol="guacamole")
    client = GuacamoleClient(
        "74.207.234.105",
        4822,
        {
            "protocol": "ssh",
            "size": [1024, 768, 96],
            "audio": [],
            "video": [],
            "image": [],
            "args": {
                "hostname": "2.tcp.ngrok.io",
                "port": 10220,
            },
        },
        debug=True
    )

    asyncio.get_event_loop().create_task(socket_to_client(websocket, client))

    while True:
        data = await websocket.receive_text()
        instruction = Instruction.from_string(data)
        await client.send(str(instruction))
