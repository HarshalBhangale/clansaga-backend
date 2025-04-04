from pydapper import connect
from database.connection_string import connection_string
from models.user_models import Clan
from datetime import datetime


def is_user_in_clan(user_id: int) -> bool:
    """Check if a user is already in a clan"""
    with connect(connection_string) as commands:
        result = commands.query_single(
            "SELECT clan_id FROM Users WHERE user_id = ?user_id?",
            param={"user_id": user_id}
        )
        return result and result.get("clan_id") is not None


def insert_clan(clan: Clan) -> int:
    """Insert a new clan and return its ID"""
    with connect(connection_string) as commands:
        command = """
        INSERT INTO Clans (clan_name, clan_image, created_at, updated_at, clan_leader_id)
        VALUES (?clan_name?, ?clan_image?, ?created_at?, ?updated_at?, ?clan_leader_id?)
        """
        commands.execute(
            command,
            param={
                "clan_name": clan.clan_name,
                "clan_image": clan.clan_image,
                "created_at": clan.created_at,
                "updated_at": clan.updated_at,
                "clan_leader_id": clan.clan_leader_id
            }
        )
        
        # Get the last inserted id
        result = commands.query_single("SELECT last_insert_rowid() as clan_id")
        return result["clan_id"]


def get_clan_by_id(clan_id: int):
    """Get clan details by clan ID"""
    with connect(connection_string) as commands:
        clan = commands.query_single(
            """
            SELECT c.*, u.username as leader_name, u.wallet_address as leader_wallet
            FROM Clans c
            JOIN Users u ON c.clan_leader_id = u.user_id
            WHERE c.clan_id = ?clan_id?
            """,
            param={"clan_id": clan_id}
        )
        return clan


def join_clan_by_id(user_id: int, clan_id: int):
    """Update a user to join a clan"""
    with connect(connection_string) as commands:
        commands.execute(
            "UPDATE Users SET clan_id = ?clan_id?, updated_at = ?updated_at? WHERE user_id = ?user_id?",
            param={
                "clan_id": clan_id,
                "updated_at": datetime.now(),
                "user_id": user_id
            }
        )


def get_clan_id_by_invite_code(invite_code: str) -> int:
    """Get the clan ID associated with an invite code"""
    with connect(connection_string) as commands:
        result = commands.query_single(
            "SELECT clan_id FROM Referrals WHERE referral_code = ?referral_code? AND is_active = TRUE",
            param={"referral_code": invite_code}
        )
        if not result or result.get("clan_id") is None:
            raise ValueError(f"No active clan found for invite code: {invite_code}")
        return result["clan_id"]


def get_available_clans():
    """Get all available clans with member counts"""
    with connect(connection_string) as commands:
        clans = commands.query(
            """
            SELECT c.*, u.username as leader_name, u.wallet_address as leader_wallet,
                  (SELECT COUNT(*) FROM Users WHERE clan_id = c.clan_id) as member_count
            FROM Clans c
            JOIN Users u ON c.clan_leader_id = u.user_id
            """
        )
        return clans



def get_user_clan(user_id: int):
    """Get the clan a user belongs to"""
    try:
        with connect(connection_string) as commands:
            # First check if user is in a clan
            user_check = commands.query_single(
                "SELECT clan_id FROM Users WHERE user_id = ?user_id?",
                param={"user_id": user_id}
            )
            
            if not user_check or user_check.get("clan_id") is None:
                return None
                
            # Now get the clan details
            clan = commands.query_single(
                """
                SELECT c.*, u.username as leader_name, u.wallet_address as leader_wallet,
                    (SELECT COUNT(*) FROM Users WHERE clan_id = c.clan_id) as member_count
                FROM Clans c
                JOIN Users u ON c.clan_leader_id = u.user_id
                WHERE c.clan_id = ?clan_id?
                """,
                param={"clan_id": user_check["clan_id"]}
            )
            return clan
    except Exception as e:
        print(f"Error in get_user_clan: {str(e)}")
        return None

def get_clan_members(clan_id: int):
    """Get all members of a clan"""
    with connect(connection_string) as commands:
        members = commands.query(
            """
            SELECT user_id, wallet_address, username, profile_image, created_at
            FROM Users
            WHERE clan_id = ?clan_id?
            """,
            param={"clan_id": clan_id}
        )
        return members