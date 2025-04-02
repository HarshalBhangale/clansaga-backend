from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    token: str
    created_at: datetime
    updated_at: datetime
    clan_id: Optional[int] = None


class Clan(BaseModel):
    clan_name: str
    clan_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    clan_leader_id: int


class ClanCreation(BaseModel):
    clan_name: str
    clan_image: Optional[str] = None
    creator_email: EmailStr


class JoinClan(BaseModel):
    user_email: EmailStr
    clan_id: Optional[int] = None
    invite_code: Optional[str] = None