from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session

#classe base para Pessoa - contém os campos comuns de uma pessoa. 
class PessoaBase(SQLModel):
    name: str
    age: int = Field(ge=0, le=120)
    email: str

class Pessoa(PessoaBase, table=True): #representa a tabela pessoa no banco
    id: Optional[int] = Field(default=None, primary_key=True)
    enderecos: List["Endereco"] = Relationship(back_populates="pessoa")

class EnderecoBase(SQLModel):
    logradouro: str
    numero: int
    estado: str
    cidade: str
    bairro: str

class Endereco(EnderecoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: Optional[int] = Field(default=None, foreign_key="pessoa.id")
    pessoa: Optional[Pessoa] = Relationship(back_populates="enderecos")

# Use a file-based SQLite DB for development so the DB persists across reloads/processes.
DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session