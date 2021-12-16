from __future__ import annotations

from functools import lru_cache

from pydantic import BaseConfig, BaseModel, BaseSettings, HttpUrl


def to_camel(string: str) -> str:
    first, *rest = string.split("_")
    return first + "".join(word.capitalize() for word in rest)


class CamelcaseBaseModel(BaseModel):
    class Config(BaseConfig):
        alias_generator = to_camel
        allow_population_by_field_name = True


class Settings(BaseSettings):
    onos_api_url: HttpUrl = HttpUrl("http://localhost:8181/onos/v1/", scheme="http", host="localhost")
    onos_user: str = "onos"
    onos_pass: str = "rocks"



@lru_cache
def get_settings() -> Settings:
    return Settings()
