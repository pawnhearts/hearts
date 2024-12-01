import asyncio
import random
from collections import deque
from datetime import datetime
from decimal import Decimal
from weakref import WeakValueDictionary
from typing import Annotated, TypedDict

from beanie import Document, Indexed
from bson import ObjectId
from faker import Faker
from pydantic import Field, BaseModel, ValidationError, PlainSerializer, computed_field, field_serializer
from pydantic_core.core_schema import SerializationInfo

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

    @property
    def player(self):
        if self.telegram_id not in players:
            players[self.telegram_id] = Player(telegram_id=self.telegram_id, user_id=self._id, display_name=self.display_name or self.username)
        return players[self.telegram_id]

players = WeakValueDictionary()

class Player(BaseModel):
    telegram_id: int
    user_id: ObjectId | None = None
    display_name: str = None
    hand: list[str] = Field(default_factory=list, exclude=True)
    pass_cards: list[str] = Field(default_factory=list, exclude=True)
    scores: list[int] = Field(default_factory=list)
    auto_move: bool = False
    is_bot: bool = False

    async def get_user(self):
        return await User.get(self.user_id)

    @classmethod
    def get_bot(cls) -> 'Player':
        return Player(telegram_id=0, auto_move=True, display_name=Faker().name(), is_bot=True)


class Chat(BaseModel):
    player: PlayerRef
    text: str
    private_to: PlayerRef | None = None
    created_at: datetime = Field(default_factory=datetime.now)


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
    _pass_names = ['left', 'right', 'across', '']
    _votes: set[PlayerRef] = Field(default_factory=set)
    chat_messages: list[Chat] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = None
    waiting_for_pass: bool = False
    _public_methods = {'chat', 'player_move', 'pass_cards'}


    @field_serializer('chat_messages')
    def get_chat_messages(self, v: list[Chat], info: SerializationInfo) -> list[Chat]:
        player = info.context.get('player')
        return [chat for chat in self.chat_messages if not chat.private_to or chat.player == player]

    async def chat(self, player: Player, chat: Chat):
        chat.player = player
        await self.notify('chat', chat.private_to, chat.model_dump())

    async def join(self, player: Player):
        self.players.append(player)
        players[player.telegram_id] = player
        games_by_player[player.telegram_id] = self
        await self.notify('joined', None, player.model_dump())
        for pl in self.players:
            await self.notify('joined', player, pl.model_dump())

        if len(self.players) == 4:
            await self.start()

        await self.notify_state(player)

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
        await self.notify('left', None, player.model_dump())


    async def start(self):
        self.started_at = datetime.now()

        await self.notify('start', None, {})
        await self.deal()

    async def vote_to_start(self, player: PlayerRef):
        self._votes.add(player)
        if len(self._votes) == len(self.players) > 1:
            while len(self.players) < 4:
                await self.join(Player.get_bot())
            await self.start()

    async def notify(self, event: str, player: Player | None, data: dict) -> None:
        from ws import manager

        msg = Notification(event=event, player=player, data=data)
        if player:
            await manager.notify_player(player, msg)
        else:
            await manager.notify_game(self, msg)

        print(msg.model_dump())

    async def notify_state(self, player: Player) -> None:
        from ws import manager

        msg = Notification(event='state', player=player, data=self.model_dump(context={'player': player}))
        await manager.notify_player(player, msg)

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
            await self.notify('hand', p, p.model_dump(include={'hand'}))
            p.scores.append(0)

        for i, p in self.players:
            if '2c' in p.hand:
                self.players.rotate(-i)
                await self.notify('players', None, self.model_dump(include={'players'}))
                break
        if pass_to := self._pass_to[self.round_number % 4]:
            self.waiting_for_pass = True
            for p in self.players:
                p.pass_cards = []
            await asyncio.sleep(5)
            for i, p in enumerate(self.players):
                self.players[(i+pass_to) % 4].hand.extend(
                    p.pass_cards or [p.hand.pop(random.randint(0, len(p.hand))) for _ in range(3)]
                )
                await self.notify('pass', p, {'to': self.players[(i+pass_to) % 4].id, 'where': self._pass_names[self.round_number % 4]})
                p.pass_cards = []
            for p in self.players:
                await self.notify('hand', p, p.model_dump(include={'hand'}))
            self.waiting_for_pass = False


        self.round_number += 1

    async def player_move(self, player: Player, card):
        if self.players[len(self.table)] != player:
            raise ValidationError('Not your move')
        await self.move(card)

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
        await self.notify('table', None, self.model_dump(include={'table'}))
        if len(self.table) == 4:
            scores = sum(map(score, self.table))
            if scores:
                self.score_opened = True
            took = max_rank(self.table)
            # notify
            await self.notify('took', None, {'took': self.players[took].id, 'score': scores})
            self.players[took].scores[-1] += scores
            self.players.rotate(-took)
            await self.notify('players', None, self.model_dump(include={'players'}))
            self.table = []
            if not any(p.hand for p in self.players):
                await self.deal()

        await self.notify('table', None, self.model_dump(include={'table'}))
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
        if not self.waiting_for_pass:
            raise ValidationError('Cannot pass cards')
        for card in cards:
            try:
                player.hand.pop(player.hand.index(card))
            except ValueError:
                raise ValidationError("You don't have that card")
