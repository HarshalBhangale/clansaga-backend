from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    wallet_address: str
    username: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    clan_id: Optional[int] = None


class Clan(BaseModel):
    clan_name: str
    clan_image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    clan_leader_id: int


class ClanCreation(BaseModel):
    clan_name: str
    clan_image: Optional[str] = None
    creator_wallet: str


class JoinClan(BaseModel):
    wallet_address: str
    clan_id: Optional[int] = None
    invite_code: Optional[str] = None