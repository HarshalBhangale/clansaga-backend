from fastapi import APIRouter, HTTPException, Response, Body
from datetime import datetime
from models.user_models import Clan, ClanCreation, JoinClan
from database.database_queries import (
    user_exists, 
    fetch_user_by_wallet
)
from database.clan_database_queries import (
    is_user_in_clan, 
    insert_clan, 
    get_clan_by_id,
    join_clan_by_id,
    get_available_clans,
    get_user_clan,
    get_clan_id_by_invite_code,
    get_clan_members,
    remove_user_from_clan,
    is_clan_leader,
)
from services.referral_system import is_active_referral_code
from services.clan_referral_system import generate_clan_invite_code
from pydantic import BaseModel
import time

router = APIRouter()

# Simple in-memory cache
_cache = {}
CACHE_TTL = 30  # seconds
class LeaveClanRequest(BaseModel):
    wallet_address: str

@router.post("/create_clan")
async def create_clan(clan_details: ClanCreation):
    """Create a new clan with the user as the leader"""
    if not user_exists(clan_details.creator_wallet):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_wallet(clan_details.creator_wallet)
    
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
    invite_code = generate_clan_invite_code(clan_id, user_id)
    
    # Update user to be part of the clan
    join_clan_by_id(user_id, clan_id)
    
    return {
        "message": "Clan created successfully",
        "clan_id": clan_id,
        "invite_code": invite_code
    }


@router.post("/join_clan")
async def join_clan(join_details: JoinClan):
    """Join a clan using either an invite code or clan ID"""
    if not user_exists(join_details.wallet_address):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_wallet(join_details.wallet_address)
    
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
    """Get all available clans"""
    clans = get_available_clans()
    return {"clans": clans}


@router.get("/user_clan/{wallet_address}")
async def user_clan(wallet_address: str, response: Response):
    """Get the clan a user belongs to with caching"""
    cache_key = f"clan_{wallet_address}"
    current_time = time.time()
    
    # Check cache first
    if cache_key in _cache and (current_time - _cache[cache_key]["timestamp"] < CACHE_TTL):
        return _cache[cache_key]["data"]
    
    # Not in cache, process normally
    if not user_exists(wallet_address):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_wallet(wallet_address)
    clan = get_user_clan(user_id)
    
    if not clan:
        result = {"message": "User is not part of any clan"}
    else:
        result = {"clan": clan}
    
    # Store in cache
    _cache[cache_key] = {
        "data": result,
        "timestamp": current_time
    }
    
    # Add cache control headers
    response.headers["Cache-Control"] = f"max-age={CACHE_TTL}"
    return result


@router.get("/clan/{clan_id}/members")
async def clan_members(clan_id: int):
    """Get all members of a clan"""
    clan = get_clan_by_id(clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    
    members = get_clan_members(clan_id)
    return {"members": members, "count": len(members)}


@router.post("/generate_invite/{wallet_address}")
async def generate_invite(wallet_address: str):
    """Generate a new invite code for the user's clan (if they are the leader)"""
    print(f"Generating invite code for wallet address: {wallet_address}")
    
    try:
        # Check if user exists
        if not user_exists(wallet_address):
            print(f"User not found for wallet address: {wallet_address}")
            return {"error": "User not found", "status": 404}
        
        # Get user ID from wallet address
        user_id = fetch_user_by_wallet(wallet_address)
        print(f"Found user ID: {user_id}")
        
        # Get user's clan
        clan = get_user_clan(user_id)
        if not clan:
            print(f"User {user_id} is not part of any clan")
            return {"error": "User is not part of any clan", "status": 404}
        
        print(f"Found clan: {clan['clan_id']} for user {user_id}")
        
        # Check if user is clan leader
        if str(clan["clan_leader_id"]) != str(user_id):
            print(f"User {user_id} is not the leader of clan {clan['clan_id']}")
            return {
                "error": "Only clan leaders can generate invite codes",
                "status": 403,
                "is_clan_leader": False,
                "clan_name": clan.get("clan_name", "Unknown clan"),
                "clan_id": clan.get("clan_id")
            }
        
        # Generate new invite code
        invite_code = generate_clan_invite_code(clan["clan_id"], user_id)
        print(f"Generated invite code: {invite_code} for clan {clan['clan_id']}")
        
        return {
            "message": "Invite code generated successfully",
            "invite_code": invite_code,
            "status": 200,
            "clan_id": clan["clan_id"],
            "clan_name": clan.get("clan_name", "Unknown clan")
        }
    except Exception as e:
        print(f"Error generating invite code: {str(e)}")
        # Only create a 500 error for unexpected exceptions, not for normal validation failures
        if isinstance(e, HTTPException):
            # Re-raise HTTP exceptions as-is
            raise e
        else:
            # For other unexpected errors
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        

@router.post("/leave_clan")
async def leave_clan(request: LeaveClanRequest):
    """Allow a user to leave their current clan"""
    if not user_exists(request.wallet_address):
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = fetch_user_by_wallet(request.wallet_address)
    clan = get_user_clan(user_id)
    
    if not clan:
        raise HTTPException(status_code=400, detail="User is not part of any clan")
    
    # Check if user is the clan leader
    if clan["clan_leader_id"] == user_id:
        raise HTTPException(status_code=400, detail="Clan leader cannot leave the clan. You must transfer leadership or disband the clan.")
    
    # Remove user from clan
    remove_user_from_clan(user_id)
    
    # Clear user clan cache
    cache_key = f"clan_{request.wallet_address}"
    if cache_key in _cache:
        del _cache[cache_key]
    
    return {"message": "Successfully left the clan"}

@router.post("/remove_member")
async def remove_clan_member(leader_wallet: str = Body(...), member_wallet: str = Body(...)):
    """Allow a clan leader to remove a member from their clan"""
    # Verify both users exist
    if not user_exists(leader_wallet):
        raise HTTPException(status_code=404, detail="Leader not found")
    
    if not user_exists(member_wallet):
        raise HTTPException(status_code=404, detail="Member not found")
    
    leader_id = fetch_user_by_wallet(leader_wallet)
    member_id = fetch_user_by_wallet(member_wallet)
    
    # Get clan info
    leader_clan = get_user_clan(leader_id)
    member_clan = get_user_clan(member_id)
    
    if not leader_clan:
        raise HTTPException(status_code=400, detail="Leader is not part of any clan")
    
    if not member_clan:
        raise HTTPException(status_code=400, detail="Member is not part of any clan")
    
    # Verify they're in the same clan
    if leader_clan["clan_id"] != member_clan["clan_id"]:
        raise HTTPException(status_code=400, detail="Leader and member are not in the same clan")
    
    # Verify the leader is actually the clan leader
    if leader_clan["clan_leader_id"] != leader_id:
        raise HTTPException(status_code=403, detail="Only clan leaders can remove members")
    
    # Cannot remove yourself
    if leader_id == member_id:
        raise HTTPException(status_code=400, detail="Leader cannot remove themselves from the clan")
    
    # Remove member from clan
    remove_user_from_clan(member_id)
    
    # Clear member's clan cache
    cache_key = f"clan_{member_wallet}"
    if cache_key in _cache:
        del _cache[cache_key]
    
    return {"message": "Successfully removed member from clan"}