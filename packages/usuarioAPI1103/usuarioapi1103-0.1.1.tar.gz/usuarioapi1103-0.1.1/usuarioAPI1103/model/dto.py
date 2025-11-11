from typing import List, Optional
from sqlmodel import Field
from usuarioAPI1103.model.models import PessoaBase, EnderecoBase

# ---------- PESSOA ----------
class PessoaCreate(PessoaBase):
    pass

class PessoaRead(PessoaBase):
    id: int
    enderecos: List["EnderecoRead"] = []
    model_config = {"from_attributes": True}

class PessoaUpdate(PessoaBase):
    nome: Optional[str] = None
    idade: Optional[int] = None
    email: Optional[str] = None

# ---------- ENDERECO ----------
class EnderecoCreate(EnderecoBase):
    pessoa_id: int  # obrigatório ter uma pessoa para ligar com

class EnderecoRead(EnderecoBase):
    id: int
    pessoa_id: int
    model_config = {"from_attributes": True}

class EnderecoUpdate(EnderecoBase):
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
