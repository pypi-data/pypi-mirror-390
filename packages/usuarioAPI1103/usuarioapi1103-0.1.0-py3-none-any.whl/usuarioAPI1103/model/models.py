from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# ---------- Pessoa ----------
class PessoaBase(SQLModel):
    nome: str = Field(min_length=2, max_length=120)
    idade: int = Field(ge=0, le=120)
    email: str = Field(min_length=5, max_length=100)

class Pessoa(PessoaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # back_populates liga Pessoa <-> Endereço
    enderecos: List["Endereco"] = Relationship(back_populates="pessoa")


# ---------- HERO ----------
class EnderecoBase(SQLModel):
    logradouro :str = Field(min_length=2, max_length=150)
    numero     :str = Field(min_length=1, max_length=10)
    estado     :str = Field(min_length=2, max_length=50)
    cidade     :str = Field(min_length=2, max_length=100)
    bairro     :str = Field(min_length=2, max_length=100)

class Endereco(EnderecoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pessoa_id: int = Field(foreign_key="pessoa.id", index=True)
    pessoa: Optional[Pessoa] = Relationship(back_populates="enderecos")
