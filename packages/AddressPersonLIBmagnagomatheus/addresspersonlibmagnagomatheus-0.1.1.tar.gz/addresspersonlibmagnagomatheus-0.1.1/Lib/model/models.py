from typing import Optional, List, Annotated
from sqlmodel import SQLModel, Field, Relationship

### SQLModel Classes creating

# ---------- ADDRESS ----------

# Address has to be on top because the python read top to bottom...

class AddressBase(SQLModel):
    logradouro: str = Field(index=True)
    numero: int = Field(index=True)
    estado: str = Field(index=True)
    cidade: str = Field(index=True)
    bairro: str = Field(index=True) 

# Creating the Address class to relate to Person
class Address(AddressBase, table=True):
    address_id: int | None = Field(default=None, primary_key = True, index=True)
    #back_populates liga Address e Person
    person: Optional["Person"] = Relationship(back_populates="address")


# ---------- PERSON ----------

# Criando a classe Pessoa para conexao com banco de dados, usando SQLModel
# table = true --> Tells SQLModel that it should represent a table in the SQL database.

class PersonBase(SQLModel):
    # Field(index = True) make SQLModel create a SQL index for this column (attribute)
    name: str = Field(index=True)

class Person(PersonBase, table=True):
    # Field(primary_key = True) tells that the ID is the primary key in the SQL database
    person_id: int | None = Field(default=None, primary_key = True, index=True)
    
    #foreing key from address
    address_id: int = Field(foreign_key="address.address_id")

    # relation
    #back_populates liga Person e Address
    address: Optional[Address] = Relationship(back_populates="person")