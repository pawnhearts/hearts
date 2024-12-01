import hmac
from typing import Optional
from xml.sax import parse

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from fastapi.params import Cookie
from fastapi.responses import HTMLResponse
from pygments.lexers import q
from starlette import status

from config import config
from models import Game, Player, games_by_player, Notification, User

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

    async def connect(self, websocket: WebSocket, telegram_id: int):
        await websocket.accept()
        self.sockets[telegram_id] = websocket
        # user = await User.get_or_create(telegram_id=telegram_id)
        # player = user.player
        player = Player(telegram_id=telegram_id, display_name=f'a{telegram_id}')
        if self.open_game.started_at:
            self.open_game = Game()
        await self.open_game.join(player)
        websocket.game = self.open_game
        websocket.player = player
        if self.open_game.started_at:
            self.open_game = Game()

    async def disconnect(self, websocket: WebSocket):
        if game := games_by_player[websocket.player.telegram_id]:
            await game.leave(websocket.player)

        for k, v in self.sockets.items():
            if v == websocket:
                del self.sockets[k]
                break

    async def notify_game(self, game: Game, notification: Notification):
        for player in game.players:
            await self.notify_player(player, notification)

    async def notify_player(self, player: Player, notification: Notification):
        try:
            await self.sockets[player.telegram_id].send_text(notification.model_dump_json())
        except:
            self.sockets.pop(player.telegram_id, None)

manager = ConnectionManager()


@ws_router.get("/")
async def get():
    return HTMLResponse(html)


@ws_router.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):#, key: Optional[str] = Cookie(None)):
    # digest = hmac.new(config.secret_key.encode(), str('telegram_id').encode(), 'sha256').hexdigest()
    # if not hmac.compare_digest(key, digest):
    #     return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    await manager.connect(websocket, telegram_id)
    try:
        while True:
            data = await websocket.receive_json()
            method = data.pop('method')
            data['player'] = websocket.player
            if method in Game._public_methods:
                await getattr(websocket.game, method)(**data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)