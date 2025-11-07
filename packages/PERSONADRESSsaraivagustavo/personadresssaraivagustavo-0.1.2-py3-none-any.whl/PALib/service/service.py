# app/services/base.py
from typing import Generic, TypeVar, List, Any, Optional
from sqlmodel import Session, SQLModel
from PALib.repository.base import Repository, ModelT, CreateT, UpdateT

class Service(Generic[ModelT, CreateT, UpdateT]):
    def __init__(self, repo: Repository[ModelT, CreateT, UpdateT]): # recebe o repository que vai usar como parâmetro, o service não precisa saber detalhes de como o repository funciona, só precisa saber que ele tem os métodos certos e usar
        self.repo = repo

    #=============== CRUD ===============
    #método pra buscar um registro pelo id
    def get(self, session: Session, id: Any) -> Optional[ModelT]:
        return self.repo.get(session, id)

    #------------------------------------
    #método pra listar todos os registros, com paginação (offset e limit)
    def list(self, session: Session, offset: int = 0, limit: int = 100) -> List[ModelT]:
        return self.repo.list(session, offset, limit)

    #------------------------------------
    #método pra criar um novo registro
    def create(self, session: Session, data: CreateT) -> ModelT:
        return self.repo.create(session, data)

    #------------------------------------
    #método pra atualizar um registro
    def update(self, session: Session, id: Any, data: UpdateT) -> ModelT:
        obj = self.repo.get(session, id)
        if not obj:
            raise ValueError("Not found")
        return self.repo.update(session, obj, data)

    #------------------------------------
    #método pra deletar um registro
    def delete(self, session: Session, id: Any) -> None:
        obj = self.repo.get(session, id)
        if not obj:
            raise ValueError("Not found")
        return self.repo.delete(session, obj)
