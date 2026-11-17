import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError

from app.auth.models import AuthenticatedUser


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "local-development-secret-change-me",
)

JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AuthenticatedUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        email = payload.get("email")
        roles = payload.get("roles", [])

        if not user_id or not email:
            raise credentials_error

        return AuthenticatedUser(
            user_id=str(user_id),
            email=str(email),
            roles=roles,
        )

    except PyJWTError as error:
        raise credentials_error from error
