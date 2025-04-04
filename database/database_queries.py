import datetime

from pydapper import connect
from database.connection_string import connection_string
from models.user_models import User


def fetch_user_by_wallet(wallet_address: str) -> int:
    """Get user_id from wallet address"""
    try:
        with connect(connection_string) as commands:
            user_id_dict = commands.query_single(
                "SELECT user_id FROM Users WHERE wallet_address = ?wallet_address?", 
                param={"wallet_address": wallet_address})
            return user_id_dict["user_id"]
    except Exception as e:
        print(f"Error fetching user by wallet: {str(e)}")
        raise ValueError(f"User with wallet address {wallet_address} not found")


def insert_user(user_details: User):
    """Insert a new user into the database"""
    with connect(connection_string) as commands:
        commands.execute(
            """
            INSERT INTO Users(wallet_address, username, profile_image, created_at, updated_at) 
            VALUES(?wallet_address?, ?username?, ?profile_image?, ?created_at?, ?updated_at?)
            """,
            param={
                "wallet_address": user_details.wallet_address,
                "username": user_details.username,
                "profile_image": user_details.profile_image,
                "created_at": user_details.created_at,
                "updated_at": user_details.updated_at
            })


def user_exists(wallet_address: str) -> bool:
    """Check if a user with the given wallet address exists"""
    with connect(connection_string) as commands:
        result = commands.query(
            "SELECT user_id FROM Users WHERE wallet_address = ?wallet_address?", 
            param={"wallet_address": wallet_address})
        return len(result) > 0


def fetch_referral_code(wallet_address: str) -> str:
    """Get the referral code for a user"""
    if user_exists(wallet_address):
        with connect(connection_string) as commands:
            # Modified to get the most recent referral code
            referral_codes = commands.query(
                """
                SELECT referral_code 
                FROM Users INNER JOIN Referrals ON Users.user_id = Referrals.user_id 
                WHERE wallet_address = ?wallet_address? AND is_active = TRUE
                ORDER BY Referrals.created_at DESC
                """,
                param={"wallet_address": wallet_address})
            
            if not referral_codes:
                raise ValueError("No active referral codes found for this wallet")
            
            # Return the most recent referral code
            return referral_codes[0]["referral_code"]
    else:
        raise ValueError(f"User with wallet address {wallet_address} does not exist")


def store_referral_code(referral_code, user_id: int):
    """Store a referral code for a user"""
    with connect(connection_string) as commands:
        commands.execute(
            """
            INSERT INTO Referrals (referral_code, created_at, user_id, is_active) 
            VALUES(?referral_code?, ?created_at?, ?user_id?, ?is_active?)
            """,
            param={
                "referral_code": referral_code, 
                "created_at": datetime.datetime.now(), 
                "user_id": user_id,
                "is_active": True
            })


def inactivate_referral_token(code):
    """Mark a referral code as inactive"""
    with connect(connection_string) as commands:
        commands.execute(
            "UPDATE Referrals SET is_active = ?is_active? WHERE referral_code = ?referral_code?",
            param={"is_active": False, "referral_code": code})


def delete_referral_token(code):
    """Delete a referral code"""
    with connect(connection_string) as commands:
        commands.execute(
            "DELETE FROM Referrals WHERE referral_code = ?referral_code?",
            param={"referral_code": code})
        
def fetch_all_referral_codes(wallet_address: str) -> list:
    """Get all referral codes for a user"""
    if user_exists(wallet_address):
        with connect(connection_string) as commands:
            referral_codes = commands.query(
                """
                SELECT referral_code, created_at, is_active, clan_id 
                FROM Users INNER JOIN Referrals ON Users.user_id = Referrals.user_id 
                WHERE wallet_address = ?wallet_address?
                ORDER BY Referrals.created_at DESC
                """,
                param={"wallet_address": wallet_address})
            
            return referral_codes
    else:
        raise ValueError(f"User with wallet address {wallet_address} does not exist")




