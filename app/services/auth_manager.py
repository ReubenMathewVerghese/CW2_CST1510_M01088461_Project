from typing import Optional
from models.user import User
from services.database_manager import DatabaseManager
import hashlib # simple example; replace with bcrypt in real project
class SimpleHasher:
    """Very basic hasher using SHA256 (for demo only)."""

    def __init__(self, db: DatabaseManager):
        self._db = db
    def register_user(self, username: str, password: str, role: str = "user") -> None:
        """Register a new user with hashed password."""
        password_hash = SimpleHasher.hash_password(password)
        self._db.execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
        )
    def login_user(self, username: str, password: str) -> Optional[User]:
        row = self._db.fetch_one(
        "SELECT username, password_hash, role FROM users WHERE username = ?",
        (username,),
        )
        if row is None:
            return None
        
        username_db, password_hash_db, role_db = row
        if SimpleHasher.check_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)