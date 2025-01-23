from fastapi import Header, HTTPException

from app.models import User
from app.models.enums import UserRole


async def get_current_user(authorization: str = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.split(" ")[1] if " " in authorization else authorization

    if token == "admin":
        return User(id=1, name="admin", role=UserRole.ADMIN)
    elif token.startswith("user"):
        try:
            user_id = int(token.split("user")[1])
            return User(id=user_id, name=f"user{user_id}", role=UserRole.USER)
        except (ValueError, IndexError):
            raise HTTPException(status_code=401, detail="Invalid user token format")
    else:
        raise HTTPException(status_code=401, detail="Invalid token")