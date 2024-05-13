from fastapi import APIRouter, Depends, HTTPException, status
from models import schemas
from typing import Union
from typing import List
import hashlib
import binascii
import json
from Crypto.Cipher import AES
from database.database import get_db
from database.query import (
    get_my_collection,
    find_my_module_by_serial_number,
    put_my_collected_data,
    get_my_data_by_serial_number,
    get_my_user_by_id,
)
from auth.oauth2 import get_current_user
from models import schemas


router = APIRouter(tags=["Data"])


# Insert data
@router.post(
    "/data/insert",
    status_code=status.HTTP_200_OK,
)
async def data_insert(
    data: schemas.InsertData,
    db: object = Depends(get_db),
):
    modules = find_my_module_by_serial_number(
        get_my_collection(db, "account"), data.sn, data.payload.sn
    )
    try:
        if modules:
            for module in modules["modules"]:
                if data.payload.sn == module["serial_number"]:
                    try:
                        aes_key = module["aes_key"].encode()
                        sha256 = hashlib.sha256()
                        sha256.update(aes_key)
                        aes_iv = sha256.digest()[:16]

                        encrypted_base64_a2b = binascii.a2b_base64(data.payload.data)

                        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
                        decrypted = cipher.decrypt(encrypted_base64_a2b)
                        decrypted_plain = decrypted.rstrip().decode()
                        decrypted_json = json.loads(decrypted_plain)

                        try:
                            collected_data = {}
                            if decrypted_json[module["sensor_name"]]:
                                collected_data.update(
                                    {
                                        module["sensor_name"]: decrypted_json[
                                            module["sensor_name"]
                                        ]
                                    }
                                )

                            if module["battery_powered"]:
                                if decrypted_json["vol"]:
                                    collected_data.update(
                                        {"vol": decrypted_json["vol"]}
                                    )

                            if decrypted_json["time"]:
                                pass

                        except Exception as e:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid data in data payload : {}".format(
                                    str(e)
                                ),
                            )

                        signal_data = schemas.SignalInfo(
                            crcok=data.crcok, rssi=data.rssi, snr=data.snr
                        )

                        data_to_insert = schemas.DataToInsert(
                            relay_serial_number=data.sn,
                            collector_serial_number=data.payload.sn,
                            time=data.timestamp,
                            sleep_time=decrypted_json["time"],
                            signal=signal_data,
                            data=collected_data,
                        )

                        info = put_my_collected_data(
                            get_my_collection(db, "data"), data_to_insert.model_dump()
                        )

                        if info:
                            return 1
                        else:
                            raise HTTPException(
                                status_code=status.HTTP_409_CONFLICT,
                                detail="Problem in database",
                            )

                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error processing request: {}".format(str(e)),
                        )
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Module in user account not added",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error processing request: {}".format(str(e)),
        )


# Get data
@router.get(
    "/data/get",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.DataToInsert],
)
async def data_get(
    serial_number: str,
    hours: int = 1,
    get_last_record: bool = False,
    db: object = Depends(get_db),
    get_current_user: schemas.Account = Depends(get_current_user),
):
    user = get_my_user_by_id(get_my_collection(db, "account"), get_current_user.id)
    data = get_my_data_by_serial_number(
        get_my_collection(db, "data"), user, serial_number, hours, get_last_record
    )

    if data == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data not found, or module is not in user account added",
        )
    else:
        return data
