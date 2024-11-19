import asyncio
import random
from collections import deque
from datetime import datetime
from decimal import Decimal
from weakref import WeakValueDictionary
from typing import Annotated, TypedDict

from beanie import Document, Indexed
from bson import ObjectId
from pydantic import Field, BaseModel, ValidationError, PlainSerializer

PlayerRef = Annotated["Player", PlainSerializer(lambda x: x.id, return_type=int)]


def rank(card) -> int:
    return "23456789tjqka".index(card[0])


def score(card) -> int:
    if card == "qs":
        return 13
    elif card[1] == "h":
        return 1
    return 0


def max_rank(cards):
    return cards.index(max(filter(lambda c: c[1] == cards[0][1]), key=rank))


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
    async def get_or_create(cls, **data) -> 'User':
        obj = await cls.find_one(Player.telegram_id == data['telegram_id']) or cls.insert_one(**data)
        await obj.set(**data)
        return obj


class Player(BaseModel):
    telegram_id: int
    user_id: ObjectId
    hand: list[str] = None
    pass_cards: list[str] = Field(default_factory=list)
    scores: list[int] = Field(default_factory=list)
    auto_move: bool = False

    async def get_user(self):
        return await User.get(self.user_id)


class Notification(BaseModel):
    event: str
    player: PlayerRef
    data: dict
    created_at: datetime = Field(default_factory=datetime.now)


games_by_player = WeakValueDictionary()


class Game(BaseModel):
    players: deque[PlayerRef] = Field(default_factory=deque)
    score_opened: bool = False
    round_number: int = 0
    table: list[str] = Field(default_factory=list)
    _timeout: asyncio.Task | None = None
    _pass_to = [-1, 1, 2, 0]
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = None
    _waiting_for_pass: bool = False


    async def join(self, player: Player):
        self.players.append(player)
        # notify
        if len(self.players) == 4:
            await self.start()

    async def leave(self, player: Player):
        # notify
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


    async def start(self):
        self.started_at = datetime.now()

    async def notify(self, event: str, player: Player | None, data: dict) -> None:
        msg = Notification(event=event, player=player, data=data)
        print(msg.model_dump_json())


    async def deal(self):
        self.score_opened = False
        self.table = []

        if scores := [p.scores for p in self.players]:
            if any(s==26 for s in scores[-1]):
                # shoot the moon
                for p in self.players:
                    p.scores[-1] = 0 if p.scores[-1] == 26 else 26

        deck = get_deck()
        for p in self.players:
            p.hand = [deck.pop(0) for _ in range(13)]
            # notify
            p.scores.append(0)

        for i, p in self.players:
            if '2c' in p.hand:
                self.players.rotate(-i)
                break
        if pass_to := self._pass_to[self.round_number % 4]:
            self._waiting_for_pass = True
            for p in self.players:
                p.pass_cards = []
            await asyncio.sleep(5)
            for i, p in enumerate(self.players):
                self.players[(i+pass_to) % 4].hand.extend(
                    p.pass_cards or [p.hand.pop(random.randint(0, len(p.hand))) for _ in range(3)]
                )
                # notify
                p.pass_cards = []
            self._waiting_for_pass = False


        self.round_number += 1

    async def move(self, card):
        move_of = self.players[len(self.table)]
        if card not in move_of.hand:
            raise ValidationError('You don\'t have that card')
        if score(card) and not self.score_opened:
            raise ValidationError('Wrong move')
        if self.table:
            suit = self.table[0][1]
            if any(c[1] == suit for c in move_of.hand):
                if card[1] != suit:
                    raise ValidationError('Wrong suit')
        self.table.append(card)
        # notify
        if len(self.table) == 4:
            scores = sum(map(score, self.table))
            if scores:
                self.score_opened = True
            took = max_rank(self.table)
            # notify
            self.players[took].scores[-1] += scores
            self.players.rotate(-took)
            self.table = []
            if not any(p.hand for p in self.players):
                await self.deal()
        if self._timeout:
            self._timeout.cancel()
        if self.players[len(self.table)].auto_move:
            await self.auto_move()
        else:
            self._timeout = asyncio.create_task(self.timeout_task())

    async def auto_move(self):
        pass

    async def timeout_task(self):
        await asyncio.sleep(7)
        await self.auto_move()

    async def pass_cards(self, player: Player, cards):
        if not self._waiting_for_pass:
            raise ValidationError('Cannot pass cards')
        for card in cards:
            try:
                player.hand.pop(player.hand.index(card))
            except ValueError:
                raise ValidationError("You don't have that card")


