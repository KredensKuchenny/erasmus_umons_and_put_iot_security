from models import schemas
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
import pytz
import datetime


def get_my_collection(db: Database, collection: str):
    return db.get_collection(collection)


def get_my_user_by_username(collection: Collection, username: str):
    user_data = collection.find_one({"username": username})
    if user_data:
        user = schemas.AccountWithPassword(
            id=str(user_data["_id"]),
            username=user_data["username"],
            password=user_data["password"],
            modules=user_data.get("modules"),
        )
        return user
    return 0


def get_my_user_by_id(collection: Collection, user_id: str):
    user_data = collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        user = schemas.Account(
            id=str(user_data["_id"]),
            username=user_data["username"],
            modules=user_data.get("modules"),
        )
        return user
    return 0


def put_my_user(collection: Collection, user: schemas.RegisterAccount):
    user_data = user.model_dump()
    result = collection.insert_one(user_data)
    new_user_id = result.inserted_id

    return get_my_user_by_id(collection, str(new_user_id))


def update_my_user_password(collection: Collection, user: schemas.AccountWithPassword):
    result = collection.update_one(
        {"_id": ObjectId(user.id)}, {"$set": {"password": user.password}}
    )
    if result.modified_count > 0:
        return 1
    return 0


def get_my_module_by_user_id(
    collection: Collection, user_id: str, module_serial_number: str
):
    user_data = collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        modules = user_data.get("modules", [])
        for module in modules:
            if module.get("serial_number") == module_serial_number:
                return module
    return 0


def get_my_modules_by_user_id(collection: Collection, user_id: str):
    user_data = collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        modules = user_data.get("modules", [])
        return modules
    return 0


def put_my_module(
    collection: Collection, user: schemas.Account, module: schemas.Module
):
    # If we want to check all users (GOOD VULNERABILITY)
    is_existing_module = collection.find_one(
        {"modules.serial_number": module.serial_number}
    )
    if is_existing_module:
        return 0

    existing_modules = user.modules or []

    # If we want to check only one user
    # for existing_module in existing_modules:
    #     if existing_module.serial_number == module.serial_number:
    #         return 0

    module_dict = module.model_dump()
    existing_modules_dicts = [m.model_dump() for m in existing_modules]

    existing_modules_dicts.append(module_dict)

    result = collection.update_one(
        {"_id": ObjectId(user.id)}, {"$set": {"modules": existing_modules_dicts}}
    )
    if result.modified_count > 0:
        return get_my_module_by_user_id(
            collection, user.id, module_dict["serial_number"]
        )
    else:
        return 0


def delete_my_module(collection: Collection, user: schemas.Account, serial_number: str):
    existing_modules = user.modules or []

    module_deleted = False

    for existing_module in existing_modules:
        if existing_module.serial_number == serial_number:
            existing_modules.remove(existing_module)
            module_deleted = True
            break

    existing_modules_dicts = [m.model_dump() for m in existing_modules]

    result = collection.update_one(
        {"_id": ObjectId(user.id)}, {"$set": {"modules": existing_modules_dicts}}
    )

    if result.modified_count > 0 and module_deleted:
        return 1
    else:
        return 0


def find_my_module_by_serial_number(
    collection: Collection, serial_number_1: str, serial_number_2: str
):
    is_existing_module = collection.find_one(
        {
            "$and": [
                {"modules.serial_number": serial_number_1},
                {"modules.serial_number": serial_number_2},
            ]
        }
    )

    if is_existing_module:
        return is_existing_module
    else:
        return 0


def put_my_collected_data(collection: Collection, data: dict):
    try:
        collection.insert_one(data)
        return 1
    except:
        return 0


def delete_my_module_data(
    collection: Collection, user: schemas.Account, serial_number: str
):
    existing_modules = user.modules or []

    module_data_deleted = False

    for existing_module in existing_modules:
        if existing_module.serial_number == serial_number:
            collection.delete_many(
                {
                    "$or": [
                        {"relay_serial_number": serial_number},
                        {"collector_serial_number": serial_number},
                    ]
                }
            )
            module_data_deleted = True
            break

    if module_data_deleted:
        return 1
    else:
        return 0


def get_my_data_by_serial_number(
    collection: Collection,
    user: schemas.Account,
    serial_number: str,
    hours: int,
    get_last_record: bool,
):
    existing_modules = user.modules or []

    for existing_module in existing_modules:
        if existing_module.serial_number == serial_number:

            start_time = datetime.datetime.now() - datetime.timedelta(hours=hours)

            if get_last_record:
                query = {
                    "$or": [
                        {"relay_serial_number": serial_number},
                        {"collector_serial_number": serial_number},
                    ]
                }

                data = collection.find_one(query, sort=[("time", -1)])

                if data:
                    fake_data_list = []
                    fake_data_list.append(data)

                    return fake_data_list

                return []

            else:
                query = {
                    "$and": [
                        {
                            "$or": [
                                {"relay_serial_number": serial_number},
                                {"collector_serial_number": serial_number},
                            ]
                        },
                        {"time": {"$gte": start_time}},
                    ]
                }

                data = collection.find(query)

                return data

    return 0
