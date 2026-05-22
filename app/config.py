from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    admin_channel_id: int
    main_channel_id: int
    admin_user_ids: list[int] = []

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("admin_user_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str | list[int]) -> list[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


settings = Settings()  # type: ignore[call-arg]
