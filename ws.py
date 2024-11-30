from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse

from models import Game, Player, games_by_player

ws_router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.sockets: dict[int, WebSocket] = {}
        self.open_game = Game()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.sockets[1] = websocket
        player = await Player.get_or_create(telegram_id=1)
        if self.open_game.started_at:
            self.open_game = Game()
        await self.open_game.join(player)
        if self.open_game.started_at:
            self.open_game = Game()

    async def disconnect(self, websocket: WebSocket):
        player = await Player.get_or_create(telegram_id=1)
        if game := games_by_player[player]:
            await game.leave(player)

        for k, v in self.sockets.items():
            if v == websocket:
                del self.sockets[k]
                break

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.sockets.values():
            await connection.send_text(message)


manager = ConnectionManager()


@ws_router.get("/")
async def get():
    return HTMLResponse(html)


@ws_router.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{telegram_id} says: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"Client #{telegram_id} left the chat")