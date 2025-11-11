from fastapi import HTTPException
from sqlmodel import Session
from usuarioAPI1103.controller.generic import create_crud_router, Hooks
from usuarioAPI1103.model.models import Endereco, Pessoa 
from usuarioAPI1103.model.dto import EnderecoCreate, EnderecoUpdate, EnderecoRead

class EnderecoHooks(Hooks[Endereco, EnderecoCreate, EnderecoUpdate]):
    def pre_create(self, payload: EnderecoCreate, session: Session) -> None:
        # valida se a pessoa existe antes de criar o endereço
        if not session.get(Pessoa, payload.pessoa_id):
            raise HTTPException(400, "pessoa_id inválido")

    def pre_update(self, payload: EnderecoUpdate, session: Session, obj: Endereco) -> None:
        # valida se a pessoa existe antes de alterar o pessoa_id
        if getattr(payload, "pessoa_id", None) is not None:
            if not session.get(Pessoa, payload.pessoa_id):
                raise HTTPException(400, "pessoa_id inválido")
            
router = create_crud_router(
    model=Endereco,
    create_schema=EnderecoCreate,
    update_schema=EnderecoUpdate,
    read_schema=EnderecoRead,
    prefix="/enderecos",
    tags=["Endereços"],
    hooks=EnderecoHooks(),
)
