from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from services.referral_system import is_active_referral_code, redeem_referral
from database.database_queries import fetch_referral_code, fetch_all_referral_codes

router = APIRouter()

class ReferralCodeRequest(BaseModel):
    referral_code: str

class WalletAddressRequest(BaseModel):
    wallet_address: str

class EmailRequest(BaseModel):
    email: str

# Endpoint from referral_routes.py - Updated to support both Body and path parameter
@router.post("/check_referral_code_validity")
async def check_referral_code_validity(request_data: Optional[ReferralCodeRequest] = None, referral_code: Optional[str] = None):
    """Check if a referral code is valid - supports both body and path parameter"""
    try:
        # Get code from either body or path parameter
        code = None
        if request_data and request_data.referral_code:
            code = request_data.referral_code
        elif referral_code:
            code = referral_code
        else:
            raise HTTPException(status_code=400, detail="Referral code is required")
            
        return is_active_referral_code(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Referral code is not valid: {str(e)}")


# Endpoint from referral_routes.py - Updated to support both Body and path parameter
@router.post("/redeem_referral_code")
async def redeem_referral_code(request_data: Optional[ReferralCodeRequest] = None, referral_code: Optional[str] = None):
    """Redeem a referral code - supports both body and path parameter"""
    try:
        # Get code from either body or path parameter
        code = None
        if request_data and request_data.referral_code:
            code = request_data.referral_code
        elif referral_code:
            code = referral_code
        else:
            raise HTTPException(status_code=400, detail="Referral code is required")
            
        redeem_referral(code)
        return {"message": "Referral code redeemed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to redeem: {str(e)}")

