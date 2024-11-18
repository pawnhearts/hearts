from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_user: str = "beanie"
    mongo_pass: str = "beanie"
    mongo_db: str = "beanie_db"

    @property
    def mongo_dsn(self):
        return f"mongodb://{self.mongo_user}:{self.mongo_pass}@{self.mongo_host}:27017/{self.mongo_db}"

    model_config = SettingsConfigDict(env_file=".env")


config = Settings()
