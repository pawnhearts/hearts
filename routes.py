from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse
from typing import Annotated

from models import games_by_player, Game, Chat, Player, players




async def get_current_player(telegram_id: int) -> Player:
    return players.get(telegram_id)

async def get_game(player: Annotated[Player, Depends(get_current_player)]) -> Game:
    return games_by_player.get(player.telegram_id)


# api_router = APIRouter(dependencies=[Annotated[Player, Depends(get_current_player)], Annotated[Game, Depends(get_game)]])
api_router = APIRouter()


@api_router.get("/", response_class=HTMLResponse)
async def root():
    return open('static/index.html').read()

@api_router.post("/leave")
async def leave(game: Annotated[Game, Depends(get_game)]):
    await game.leave()


@api_router.post("/chat")
async def chat(msg: Chat, player: Annotated[Player, Depends(get_current_player)], game: Annotated[Game, Depends(get_game)]):
    msg.player = player
    await game.chat(msg)

@api_router.post("/move")
async def move(card: str, player: Annotated[Player, Depends(get_current_player)], game: Annotated[Game, Depends(get_game)]):
    await game.player_move(player, card)

@api_router.post("/vote_to_start")
async def vote_to_start(player: Annotated[Player, Depends(get_current_player)], game: Annotated[Game, Depends(get_game)]):
    await game.vote_to_start(player)


@api_router.post("/pass_cards")
async def pass_cards(cards: list[str], player: Annotated[Player, Depends(get_current_player)], game: Annotated[Game, Depends(get_game)]):
    await game.pass_cards(player, cards)

@api_router.post("/state")
async def get_state(game: Annotated[Game, Depends(get_game)]) -> Game:
    return game
