from Lib.model.models import PersonBase, AddressBase
from typing import  List, Optional
from sqlmodel import Field


# ---------- ADDRESS ----------
class AddressPublic(AddressBase):
    address_id: int
    model_config = {"from_attributes": True}

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    logradouro: str | None = None
    numero: int | None = None
    estado: str | None = None
    cidade: str | None = None
    bairro: str | None = None

class AddressRead(AddressBase):
    address_id:int


# ---------- PERSON ----------
class PersonPublic(PersonBase):
    person_id:int
    model_config = {"from_attributes": True}

# Create a person bonded with a address
class PersonCreate(PersonBase):
    address_id: Optional[int] = None

class PersonUpdate(PersonBase):
    name: str | None = None

class PersonRead(PersonBase):
    person_id:int
    name:str
    address_id: Optional[int] = None