from fastapi import APIRouter, Depends, HTTPException, status
from models import schemas
from typing import List
from database.database import get_db
from database.query import (
    get_my_collection,
    get_my_user_by_id,
    put_my_module,
    get_my_modules_by_user_id,
    delete_my_module,
    delete_my_module_data,
)
from auth.oauth2 import get_current_user
from models import schemas

router = APIRouter(tags=["Module"])


# Show module list
@router.get(
    "/module/list",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Module],
)
async def module_list(
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):

    modules = get_my_modules_by_user_id(
        get_my_collection(db, "account"), get_current_user.id
    )
    if modules:
        return modules

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="There are no modules in database",
    )


# Add module
@router.post(
    "/module/add",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Module,
)
async def module_add(
    module: schemas.Module,
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):

    if not module.relay and (module.sensor_name == None or module.aes_key == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="If module is not relay, you need to insert sensor name and AES key",
        )

    user = get_my_user_by_id(get_my_collection(db, "account"), get_current_user.id)
    output = put_my_module(get_my_collection(db, "account"), user, module)

    if output:
        return output

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="There is module with the same serial number in database",
    )


# Remove module
@router.delete(
    "/module/delete",
    status_code=status.HTTP_200_OK,
)
async def module_delete(
    serial_number: str,
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):
    user = get_my_user_by_id(get_my_collection(db, "account"), get_current_user.id)
    output_data = delete_my_module_data(
        get_my_collection(db, "data"), user, serial_number
    )
    output_account = delete_my_module(
        get_my_collection(db, "account"), user, serial_number
    )

    if output_account:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Module deleted",
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="There is module with the same serial number in database, or module not deleted",
    )
