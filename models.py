import asyncio
import random
from collections import deque
from datetime import datetime
from decimal import Decimal
from weakref import WeakValueDictionary
from typing import Annotated, TypedDict

from beanie import Document, Indexed

# from bson import ObjectId
from faker import Faker
from pydantic import (
    Field,
    BaseModel,
    PlainSerializer,
    computed_field,
    field_serializer,
)
from pydantic_core.core_schema import SerializationInfo

PlayerRef = Annotated[
    "Player", PlainSerializer(lambda x: x.telegram_id, return_type=int)
]


def rank(card) -> int:
    return "23456789tjqka".index(card[0])


def score(card) -> int:
    if card == "qs":
        return 13
    elif card[1] == "h":
        return 1
    return 0

def sort_hand(hand):
    return sorted(hand, key=lambda c: ('cdsh'.index(c[1]), rank(c)))


def max_rank(cards):
    return cards.index(max(filter(lambda c: c[1] == cards[0][1], cards), key=rank))


def get_deck() -> list[str]:
    l = []
    for suit in "chsd":
        for rank in "23456789tjqka":
            l.append(f"{rank}{suit}")
    random.shuffle(l)
    return l


class GameResult(TypedDict):
    ended_at: datetime
    place: int
    balance_changed: Decimal


class User(Document):
    telegram_id: int = Annotated[str, Indexed(unique=True)]
    username: str = None
    display_name: str = None
    balance: Decimal = Field(default_factory=lambda: Decimal(0))
    created_at: datetime = Field(default_factory=datetime.now)
    games_played: list[GameResult] = Field(default_factory=list)

    @classmethod
    async def get_or_create(cls, **data) -> "User":
        obj = await cls.find_one(
            Player.telegram_id == data["telegram_id"]
        ) or cls.insert_one(**data)
        await obj.set(**data)
        return obj

    @property
    def player(self):
        if self.telegram_id not in players:
            players[self.telegram_id] = Player(
                telegram_id=self.telegram_id,
                user_id=self._id,
                display_name=self.display_name or self.username,
            )
        return players[self.telegram_id]


players = WeakValueDictionary()


class Player(BaseModel):
    telegram_id: int
    # user_id: ObjectId | None = None
    display_name: str = None
    hand: list[str] = Field(default_factory=list, exclude=True)
    pass_cards: list[str] = Field(default_factory=list, exclude=True)
    scores: list[int] = Field(default_factory=list)
    auto_move: bool = False
    is_bot: bool = False

    async def get_user(self):
        return await User.get(self.user_id)

    @classmethod
    def get_bot(cls) -> "Player":
        return Player(
            telegram_id=0, auto_move=True, display_name=Faker().name(), is_bot=True
        )


class Chat(BaseModel):
    player: PlayerRef | None = None
    text: str
    private_to: PlayerRef | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class Notification(BaseModel):
    event: str
    player: PlayerRef | None = None
    data: dict
    created_at: datetime = Field(default_factory=datetime.now)


games_by_player = WeakValueDictionary()


class Game(BaseModel):
    players: deque[Player] = Field(default_factory=deque)
    score_opened: bool = False
    round_number: int = 0
    table: list[str] = Field(default_factory=list)
    _timeout: asyncio.Task | None = None
    _pass_to = [-1, 1, 2, 0]
    _pass_names = ["left", "right", "across", ""]
    votes: set[int] = Field(default_factory=set)
    chat_messages: list[Chat] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = None
    waiting_for_pass: bool = False

    @field_serializer("players")
    def get_players(self, v: deque[PlayerRef]) -> list[Player]:
        return list(self.players)

    @field_serializer("chat_messages")
    def get_chat_messages(self, v: list[Chat], info: SerializationInfo) -> list[Chat]:
        player = info.context.get("player")
        return [
            chat
            for chat in self.chat_messages
            if not chat.private_to or chat.player == player
        ]

    async def message(self, player: Player, message: str, private_to: PlayerRef|None=None):
        chat_message = Chat(player=player, text=message, private_to=private_to)
        await self.notify("chat", chat_message.private_to, chat_message.model_dump())

    async def chat(self, chat_message: Chat):
        await self.notify("chat", chat_message.private_to, chat_message.model_dump())

    async def join(self, player: Player):
        if self.started_at:
            raise ValueError('Game already started')
        self.players.append(player)
        players[player.telegram_id] = player
        games_by_player[player.telegram_id] = self
        await self.notify("joined", None, player.model_dump())

        await self.notify("players", None, self.model_dump(include={"players"}))
        await self.notify_state(player)

        if len(self.players) == 4:
            await self.start()

    async def leave(self, player: Player):
        if self.started_at:
            for p in self.players:
                if player.telegram_id == p.telegram_id:
                    p.auto_move = True
                    break
        else:
            for i, p in enumerate(self.players):
                if player.telegram_id == p.telegram_id:
                    del self.players[i]
                    break
        games_by_player.pop(player.telegram_id, None)
        await self.notify("left", None, player.model_dump())
        await self.notify("players", None, self.model_dump(include={"players"}))

    async def start(self):
        self.started_at = datetime.now()
        for player in self.players:
            await self.notify_state(player)

        await self.deal()

    async def vote_to_start(self, player: PlayerRef):
        self.votes.add(player.telegram_id)
        if len(self.votes) == len(self.players) >= 1:
            while len(self.players) < 4:
                await self.join(Player.get_bot())
            await self.start()

    async def notify(self, event: str, player: Player | None, data: dict) -> None:
        if player and player.is_bot:
            return
        from ws import manager

        msg = Notification(event=event, player=player, data=data)
        if player:
            await manager.notify_player(player, msg)
        else:
            await manager.notify_game(self, msg)

        print(msg.model_dump())

    async def notify_state(self, player: Player) -> None:
        from ws import manager

        msg = Notification(
            event="state",
            player=player,
            data=self.model_dump(context={"player": player}),
        )
        await manager.notify_player(player, msg)

    async def deal(self):
        print('DEAL')
        self.score_opened = False
        self.table = []

        if scores := [p.scores for p in self.players]:
            if any(s == 26 for s in scores[-1]):
                for p in self.players:
                    p.scores[-1] = 0 if p.scores[-1] == 26 else 26
                await self.notify('shoot_the_moon', None, {})

        deck = get_deck()
        for p in self.players:
            p.hand = [deck.pop(0) for _ in range(13)]
            await self.notify("hand", p, {"hand": sort_hand(p.hand)})
            p.scores.append(0)

        for i, p in enumerate(self.players):
            if "2c" in p.hand:
                self.players.rotate(-i)
                await self.notify("players", None, self.model_dump(include={"players"}))
                break
        if pass_to := self._pass_to[self.round_number % 4]:
            self.waiting_for_pass = True
            for p in self.players:
                p.pass_cards = []
                await self.notify(
                    "waiting_pass",
                    p,
                    {
                        "to": self.players[(i + pass_to) % 4].telegram_id,
                        "where": self._pass_names[self.round_number % 4],
                    },
                )
            await asyncio.sleep(2)
            for i, p in enumerate(self.players):
                while len(p.pass_cards) < 3:
                    card = random.choice(p.hand)
                    p.pass_cards.append(card)
                    p.hand.remove(card)
                while len(p.pass_cards) > 3:
                    p.hand.append(p.pass_cards.pop(0))
                self.players[(i + pass_to) % 4].hand.extend(p.pass_cards)
                await self.notify(
                    "pass",
                    p,
                    {
                        "to": self.players[(i + pass_to) % 4].telegram_id,
                        "where": self._pass_names[self.round_number % 4],
                        "cards": p.pass_cards,
                    },
                )
                await self.notify(
                    "got",
                    self.players[(i + pass_to) % 4],
                    {
                        "from": p,
                        "where": self._pass_names[self.round_number % 4],
                        "cards": p.pass_cards,
                    },
                )
                p.pass_cards = []
            for p in self.players:
                await self.notify("hand",p , {"hand": sort_hand(p.hand)})
            self.waiting_for_pass = False

        self.round_number += 1
        if self._timeout:
            self._timeout.cancel()
        if self.players[len(self.table)].auto_move:
            await self.auto_move()
        else:
            self._timeout = asyncio.create_task(self.timeout_task())

    async def player_move(self, player: Player, card):
        if self.players[len(self.table)] != player:
            raise ValueError("Not your move")
        await self.move(card)

    async def move(self, card):
        move_of = self.players[len(self.table)]
        if card not in move_of.hand:
            raise ValueError("You don't have that card")
        if score(card) and not self.score_opened:
            raise ValueError("Wrong move")
        if self.table:
            suit = self.table[0][1]
            if any(c[1] == suit for c in move_of.hand):
                if card[1] != suit:
                    raise ValueError("Wrong suit")
        self.table.append(card)
        move_of.hand.remove(card)
        await self.notify("table", None, self.model_dump(include={"table", "score_opened"}))
        await self.notify("hand", move_of, {"hand": sort_hand(move_of.hand)})
        if len(self.table) == 4:
            scores = sum(map(score, self.table))
            if scores:
                self.score_opened = True
            took = max_rank(self.table)
            # notify
            await self.notify(
                "took", None, {"took": self.players[took], "score": scores}
            )
            await asyncio.sleep(2)
            self.players[took].scores[-1] += scores
            self.players.rotate(-took)
            await self.notify("players", None, self.model_dump(include={"players"}))
            self.table = []
            if all(not p.hand for p in self.players):
                await self.deal()

        await self.notify("table", None, self.model_dump(include={"table", "score_opened"}))
        if self._timeout:
            self._timeout.cancel()
        if self.players[len(self.table)].auto_move:
            await self.auto_move()
        else:
            self._timeout = asyncio.create_task(self.timeout_task())

    async def auto_move(self):
        move_of = self.players[len(self.table)]
        if not self.table:
            return await self.move(min(move_of.hand, key=lambda c: (score(c), rank(c))))
        suit = self.table[0][1]
        if any(c[1] == suit for c in move_of.hand):
            return await self.move(
                min(filter(lambda c: c[1] == suit, move_of.hand), key=rank)
            )
        return await self.move(max(move_of.hand, key=lambda c: (score(c), rank(c))))

    async def timeout_task(self):
        await asyncio.sleep(7)
        await self.auto_move()

    async def pass_cards(self, player: Player, cards):
        if not self.waiting_for_pass:
            raise ValueError("Cannot pass cards")
        if len(cards) != 3:
            raise ValueError("Should be 3 cards")
        for card in cards:
            try:
                player.hand.pop(player.hand.index(card))
            except ValueError:
                raise ValueError("You don't have that card")

public_methods = (
    "message",
    "player_move",
    "pass_cards",
    "notify_state",
    "leave",
    "vote_to_start",
)
