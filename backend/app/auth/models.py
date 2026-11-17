from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    roles: list[str] = []
