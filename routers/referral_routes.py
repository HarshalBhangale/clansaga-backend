from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from services.referral_system import is_active_referral_code, redeem_referral
from database.database_queries import fetch_referral_code

router = APIRouter()

class ReferralCodeRequest(BaseModel):
    referral_code: str

class WalletAddressRequest(BaseModel):
    wallet_address: str

@router.post("/check_referral_code_validity")
async def check_referral_code_validity(request: ReferralCodeRequest):
    """Check if a referral code is valid"""
    try:
        return is_active_referral_code(request.referral_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Referral code is not valid: {str(e)}")

@router.post("/get_referral_code")
async def get_referral_code(request: WalletAddressRequest):
    """Get the referral code for a user"""
    try:
        return fetch_referral_code(request.wallet_address)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No referral code found: {str(e)}")

@router.post("/redeem_referral_code")
async def redeem_referral_code(request: ReferralCodeRequest):
    """Redeem a referral code"""
    try:
        redeem_referral(request.referral_code)
        return {"message": "Referral code redeemed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to redeem: {str(e)}")