from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.user_models import Clan, ClanCreation, JoinClan
from database.database_queries import (
    user_exists, 
    fetch_user_by_email, 
    is_user_in_clan, 
    insert_clan, 
    get_clan_by_id,
    join_clan_by_id,
    get_available_clans,
    get_user_clan
)
from services.referral_system import generate_clan_invite_code, is_active_referral_code

router = APIRouter()


@router.post("/create_clan")
async def create_clan(clan_details: ClanCreation):
    if not user_exists(clan_details.creator_email):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_email(clan_details.creator_email)
    
    if is_user_in_clan(user_id):
        raise HTTPException(status_code=400, detail="User already belongs to a clan")
    
    clan = Clan(
        clan_name=clan_details.clan_name,
        clan_image=clan_details.clan_image,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        clan_leader_id=user_id
    )
    
    clan_id = insert_clan(clan)
    invite_code = generate_clan_invite_code(clan_id)
    
    # Update user to be part of the clan
    join_clan_by_id(user_id, clan_id)
    
    return {
        "message": "Clan created successfully",
        "clan_id": clan_id,
        "invite_code": invite_code
    }


@router.post("/join_clan")
async def join_clan(join_details: JoinClan):
    if not user_exists(join_details.user_email):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_email(join_details.user_email)
    
    if is_user_in_clan(user_id):
        raise HTTPException(status_code=400, detail="User already belongs to a clan")
    
    # Join by invite code
    if join_details.invite_code:
        if not is_active_referral_code(join_details.invite_code):
            raise HTTPException(status_code=400, detail="Invalid invite code")
        
        clan_id = get_clan_id_by_invite_code(join_details.invite_code)
        join_clan_by_id(user_id, clan_id)
        
        return {"message": "Joined clan successfully via invite code"}
    
    # Join by clan_id (direct join)
    elif join_details.clan_id:
        clan = get_clan_by_id(join_details.clan_id)
        if not clan:
            raise HTTPException(status_code=404, detail="Clan not found")
        
        join_clan_by_id(user_id, join_details.clan_id)
        
        return {"message": "Joined clan successfully"}
    
    else:
        raise HTTPException(status_code=400, detail="Must provide either invite_code or clan_id")


@router.get("/available_clans")
async def available_clans():
    clans = get_available_clans()
    return {"clans": clans}


@router.get("/user_clan/{email}")
async def user_clan(email: str):
    if not user_exists(email):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_email(email)
    clan = get_user_clan(user_id)
    
    if not clan:
        return {"message": "User is not part of any clan"}
    
    return {"clan": clan}