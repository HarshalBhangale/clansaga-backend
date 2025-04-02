#!/usr/bin/env python3
import sqlite3
import os

DATABASE_FILE = 'clansaga.db'

# SQL to create the database schema
CREATE_SCHEMA_SQL = """
-- Create Users table with wallet_address as primary identifier
CREATE TABLE IF NOT EXISTS Users(
    user_id INTEGER PRIMARY KEY AutoIncrement,
    wallet_address TEXT NOT NULL UNIQUE,
    username TEXT,
    profile_image TEXT,
    created_at DATE,
    updated_at DATE,
    clan_id INTEGER
);

-- Create Clans table
CREATE TABLE IF NOT EXISTS Clans(
    clan_id INTEGER PRIMARY KEY AutoIncrement,
    clan_name TEXT NOT NULL,
    clan_image TEXT,
    created_at DATE,
    updated_at DATE,
    clan_leader_id INTEGER NOT NULL,
    foreign key(clan_leader_id) references Users(user_id)
);

-- Create Referrals table for clan invites
CREATE TABLE IF NOT EXISTS Referrals(
    referral_code_id INTEGER PRIMARY KEY AutoIncrement,
    referral_code TEXT NOT NULL,
    created_at DATE,
    is_active boolean NOT NULL,
    user_id INT NOT NULL,
    clan_id INTEGER,
    foreign key(user_id) references Users(user_id),
    foreign key(clan_id) references Clans(clan_id)
);
"""

def initialize_database():
    """Initialize the database with the required tables"""
    # Check if database file already exists
    db_exists = os.path.exists(DATABASE_FILE)
    
    # Connect to the database (creates the file if it doesn't exist)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables
    for statement in CREATE_SCHEMA_SQL.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"{'Created' if not db_exists else 'Updated'} database: {DATABASE_FILE}")


if __name__ == "__main__":
    initialize_database()