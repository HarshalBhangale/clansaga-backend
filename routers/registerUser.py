from fastapi import APIRouter, HTTPException
from models.user_models import User
from services.referral_system import referral_code_handler
from database.database_queries import user_exists, insert_user, fetch_user_by_wallet


router = APIRouter()


@router.post("/register_user")
async def register_user(user_details: User):
    """Register a new user with a wallet address"""
    if user_exists(user_details.wallet_address):
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        insert_user(user_details)
        user_id = fetch_user_by_wallet(user_details.wallet_address)
        referral_code_handler(user_id)
        return {"message": "User registered successfully", "wallet_address": user_details.wallet_address}


@router.get("/user_exists/{wallet_address}")
async def check_user_exists(wallet_address: str):
    """Check if a user with the given wallet address exists"""
    exists = user_exists(wallet_address)
    return {"exists": exists}