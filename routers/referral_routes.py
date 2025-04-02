from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from services.referral_system import is_active_referral_code, redeem_referral
from database.database_queries import fetch_referral_code, fetch_all_referral_codes

router = APIRouter()

class ReferralCodeRequest(BaseModel):
    referral_code: str

class WalletAddressRequest(BaseModel):
    wallet_address: str

@router.post("/check_referral_code_validity")
async def check_referral_code_validity(request_data: ReferralCodeRequest):
    """Check if a referral code is valid"""
    try:
        return is_active_referral_code(request_data.referral_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Referral code is not valid: {str(e)}")

@router.post("/get_referral_codes")
async def get_referral_codes(request_data: WalletAddressRequest):
    """Get all referral codes for a user"""
    try:
        codes = fetch_all_referral_codes(request_data.wallet_address)
        return {"referral_codes": codes}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No referral codes found: {str(e)}")

@router.post("/redeem_referral_code")
async def redeem_referral_code(request_data: ReferralCodeRequest):
    """Redeem a referral code"""
    try:
        redeem_referral(request_data.referral_code)
        return {"message": "Referral code redeemed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to redeem: {str(e)}")

# Add a simple test endpoint for debugging
@router.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging"""
    return {"status": "working"}