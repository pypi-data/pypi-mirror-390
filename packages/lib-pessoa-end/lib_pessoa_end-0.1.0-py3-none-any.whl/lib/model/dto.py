from typing import Optional, List
from sqlmodel import SQLModel, Field


class EndBase(SQLModel):
    logradouro: str
    numero: int
    estado: str
    cidade: str
    bairro: str
    pessoa_id: Optional[int] = None


class EndCreate(EndBase):
    pass


class EndUpdate(SQLModel):
    logradouro: Optional[str] = None
    numero: Optional[int] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    pessoa_id: Optional[int] = None


class EndRead(EndBase):
    id: int


class PessoaBase(SQLModel):
    name: str
    age: int = Field(ge=0, le=120)
    email: str


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(SQLModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None


class PessoaRead(PessoaBase):
    id: int
    enderecos: List[EndRead] = []