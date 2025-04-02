import secrets
import threading
from pydapper import connect
from database.connection_string import connection_string
from database.database_queries import store_referral_code, inactivate_referral_token, delete_referral_token

stale_time = 60 * 60 * 24 * 7  # Increase stale time to 7 days for clan invites


def generate_clan_invite_code(clan_id: int) -> str:
    """Generate an invite code for a clan and store it in the database"""
    code = secrets.token_urlsafe(8)
    store_clan_invite_code(code, clan_id)
    expire_referral_code(code)
    return code


def store_clan_invite_code(code: str, clan_id: int):
    """Store an invite code for a clan in the database"""
    with connect(connection_string) as commands:
        commands.execute(
            """
            INSERT INTO Referrals (referral_code, created_at, is_active, user_id, clan_id)
            VALUES (?referral_code?, ?created_at?, ?is_active?, 
                   (SELECT clan_leader_id FROM Clans WHERE clan_id = ?clan_id?), ?clan_id?)
            """,
            param={
                "referral_code": code,
                "created_at": datetime.now(),
                "is_active": True,
                "clan_id": clan_id
            }
        )


def is_active_clan_invite(code: str) -> bool:
    """Check if a clan invite code is active"""
    with connect(connection_string) as commands:
        result = commands.query_single(
            """
            SELECT is_active FROM Referrals 
            WHERE referral_code = ?referral_code? AND clan_id IS NOT NULL
            """,
            param={"referral_code": code}
        )
        return result and result["is_active"]


def redeem_clan_invite(code: str, user_id: int):
    """Redeem a clan invite code by adding the user to the clan"""
    with connect(connection_string) as commands:
        clan_id = commands.query_single(
            "SELECT clan_id FROM Referrals WHERE referral_code = ?referral_code?",
            param={"referral_code": code}
        )["clan_id"]
        
        commands.execute(
            "UPDATE Users SET clan_id = ?clan_id? WHERE user_id = ?user_id?",
            param={
                "clan_id": clan_id,
                "user_id": user_id
            }
        )
        
        # Optional: invalidate the code after use
        # inactivate_referral_token(code)