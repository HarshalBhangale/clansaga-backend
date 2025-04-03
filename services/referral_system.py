# services/referral_system.py - Fix the threading issue
import secrets
import threading
import time
from datetime import datetime
from pydapper import connect
from database.connection_string import connection_string
from database.database_queries import store_referral_code, inactivate_referral_token

# Increase stale time to reduce thread creation frequency
stale_time = 60 * 60 * 24 * 7  # 7 days

# Track existing expiry threads
_expiry_threads = {}
_thread_lock = threading.Lock()

def referral_code_handler(user_id: int):
    store_referral_code(generate_referral_code(), user_id)

def generate_referral_code() -> str:
    code = secrets.token_urlsafe(8)
    expire_referral_code(code)
    return code

def is_active_referral_code(code: str) -> bool:
    try:
        with connect(connection_string) as commands:
            result = commands.query_single(
                "SELECT is_active FROM Referrals WHERE referral_code = ?referral_code?",
                param={"referral_code": code})
            
            if result and result.get("is_active") is not None:
                return bool(result["is_active"])
            return False
    except Exception as e:
        print(f"Error checking referral code: {e}")
        return False

def redeem_referral(code: str):
    invalidate_referral_code(code)

def invalidate_referral_code(code: str):
    try:
        inactivate_referral_token(code)
        
        # Remove thread from tracking if exists
        with _thread_lock:
            if code in _expiry_threads:
                del _expiry_threads[code]
    except Exception as e:
        print(f"Error invalidating code: {e}")

def expire_referral_code(code: str):
    """Schedule code to expire after stale_time"""
    with _thread_lock:
        # Don't create a new thread if one already exists for this code
        if code in _expiry_threads:
            return
            
        def expire_task():
            time.sleep(stale_time)
            invalidate_referral_code(code)
            
            # Remove from tracking when done
            with _thread_lock:
                if code in _expiry_threads:
                    del _expiry_threads[code]
        
        # Create and start the thread
        t = threading.Thread(target=expire_task, daemon=True)
        t.start()
        
        # Track the thread
        _expiry_threads[code] = t