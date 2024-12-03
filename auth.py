import hmac

from config import config

from pydantic import BaseModel, computed_field, Field, model_validator, ValidationError


class UserData(BaseModel):
    telegram_id: int
    username: str

    def get_key(self) -> str:
        return hmac.new(config.secret_key.encode(), self.model_dump_json().encode(), 'sha256').hexdigest()


class UserDataOut(UserData):
    @computed_field
    def get_key(self) -> str:
        return self.get_key()


class UserDataIn(UserData):
    key: str

    @model_validator(mode='after')
    def check_key(self) -> 'UserDataIn':
        if self.key != self.get_key:
            raise ValidationError('key')
        return self
