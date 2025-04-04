import secrets
import threading
from datetime import datetime
import logging
from pydapper import connect
from database.connection_string import connection_string
from services.referral_system import expire_referral_code

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("clan_referral_system")

stale_time = 60 * 60 * 24 * 7  # 7 days for clan invites


def generate_clan_invite_code(clan_id: int, leader_id: int) -> str:
    """Generate an invite code for a clan and store it in the database"""
    logger.info(f"Generating clan invite code for clan_id={clan_id}, leader_id={leader_id}")
    try:
        code = secrets.token_urlsafe(8)
        logger.info(f"Generated code: {code}")
        
        store_clan_invite_code(code, clan_id, leader_id)
        expire_referral_code(code)
        
        logger.info(f"Successfully stored and set expiration for code: {code}")
        return code
    except Exception as e:
        logger.error(f"Error generating clan invite code: {str(e)}")
        raise


def store_clan_invite_code(code: str, clan_id: int, leader_id: int):
    """Store an invite code for a clan in the database"""
    logger.info(f"Storing clan invite code: {code} for clan_id={clan_id}, leader_id={leader_id}")
    try:
        with connect(connection_string) as commands:
            commands.execute(
                """
                INSERT INTO Referrals (referral_code, created_at, is_active, user_id, clan_id)
                VALUES (?referral_code?, ?created_at?, ?is_active?, ?user_id?, ?clan_id?)
                """,
                param={
                    "referral_code": code,
                    "created_at": datetime.now(),
                    "is_active": True,
                    "user_id": leader_id,
                    "clan_id": clan_id
                }
            )
        logger.info(f"Successfully stored invite code in database")
    except Exception as e:
        logger.error(f"Error storing clan invite code: {str(e)}")
        raise


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
        return result and result.get("is_active")


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