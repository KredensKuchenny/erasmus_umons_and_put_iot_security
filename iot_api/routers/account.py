from fastapi import APIRouter, Depends, HTTPException, status
from models import schemas
from database.database import get_db
from classes.hashing import Hash
from auth.token import create_access_token
from database.query import (
    get_my_collection,
    get_my_user_by_username,
    put_my_user,
    update_my_user_password,
)
from fastapi.security import OAuth2PasswordRequestForm
from auth.oauth2 import get_current_user
from models import schemas
from classes.verifier import Verify
from typing import Union

router = APIRouter(tags=["Account"])


# Get OAuth 2 token
@router.post("/account/login", status_code=status.HTTP_202_ACCEPTED)
async def account_login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: object = Depends(get_db),
):
    user = get_my_user_by_username(get_my_collection(db, "account"), data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if not Hash.verify_password_hash(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Register new user
@router.post(
    "/account/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Account,
)
async def account_register(user: schemas.RegisterAccount, db: object = Depends(get_db)):
    if Verify.password_verifier(user.password):
        check_username = get_my_user_by_username(
            get_my_collection(db, "account"), user.username
        )

        if not check_username:
            user.password = Hash.get_password_hash(user.password)
            new_user = put_my_user(get_my_collection(db, "account"), user)
            return new_user

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exist",
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Your password must contains at least 8 characters, one uppercase and lowercase letter, at least one digit and special character",
    )


# Show account information
@router.get(
    "/account/info",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Account,
)
async def account_info(
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):
    return get_current_user


# User password change
@router.put(
    "/account/change/password",
    status_code=status.HTTP_200_OK,
    response_model=Union[dict, int],
)
async def account_change_password(
    data: schemas.ChangePassword,
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):
    user = get_my_user_by_username(
        get_my_collection(db, "account"), get_current_user.username
    )

    if Hash.verify_password_hash(data.old_password, user.password):
        if Verify.password_verifier(data.new_password):
            user.password = Hash.get_password_hash(data.new_password)

            return update_my_user_password(get_my_collection(db, "account"), user)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your new password must contains at least 8 characters, one uppercase and lowercase letter, at least one digit and special character",
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect old password",
    )
