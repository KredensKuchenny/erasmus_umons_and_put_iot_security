from pydantic import BaseModel, Field
from typing import List
import datetime


class TokenData(BaseModel):
    username: str | None = None


class Module(BaseModel):
    serial_number: str = Field(min_length=4)
    friendly_name: str = Field(min_length=4)
    aes_key: str | None = Field(None, min_length=32, max_length=32)
    battery_powered: bool
    relay: bool
    sensor_name: str | None = Field(None, min_length=2)


class Account(BaseModel):
    id: str
    username: str
    modules: List[Module] | None = None


class AccountWithPassword(BaseModel):
    id: str
    username: str
    password: str
    modules: List[Module] | None = None


class RegisterAccount(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=8)


class ChangePassword(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class InsertDataPayload(BaseModel):
    sn: str
    data: str


class InsertData(BaseModel):
    sn: str
    crcok: bool
    rssi: float
    snr: float
    timestamp: datetime.datetime
    payload: InsertDataPayload


class SignalInfo(BaseModel):
    crcok: bool
    rssi: float
    snr: float


class DataToInsert(BaseModel):
    relay_serial_number: str
    collector_serial_number: str
    time: datetime.datetime
    sleep_time: int
    signal: SignalInfo
    data: dict
