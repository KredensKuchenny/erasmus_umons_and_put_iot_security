from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated
from auth.token import verify_token
from database.query import get_my_collection, get_my_user_by_username
from database.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: object = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token, credentials_exception)
    user = get_my_user_by_username(get_my_collection(db, "account"), token_data.username)
    
    if user is None:
        raise credentials_exception

    return user
