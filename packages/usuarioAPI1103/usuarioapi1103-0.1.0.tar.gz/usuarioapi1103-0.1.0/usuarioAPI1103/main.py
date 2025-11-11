from fastapi import FastAPI
from usuarioAPI1103.util.database import init_db
from usuarioAPI1103.controller.pessoa import router as pessoas_router
from usuarioAPI1103.controller.endereco import router as enderecos_router

app = FastAPI(title="FastAPI + SQLModel - MVC + Repository")

init_db()

app.include_router(pessoas_router)
app.include_router(enderecos_router)

@app.get("/")
def health():
    return {"status": "ok"}
