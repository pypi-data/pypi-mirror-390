# app/repositories/base.py
from typing import Generic, Type, TypeVar, Optional, List, Any
from sqlmodel import SQLModel, Session, select

ModelT = TypeVar("ModelT", bound=SQLModel) #modelo daa tabela (Pessoa, Endereco)
CreateT = TypeVar("CreateT", bound=SQLModel) #DTO para criar o modelo (PessoaCreate, EnderecoCreate)
UpdateT = TypeVar("UpdateT", bound=SQLModel) #DTO para atualizar o modelo (PessoaUpdate, EnderecoUpdate)

class Repository(Generic[ModelT, CreateT, UpdateT]): #dependendo do modelo que receber, o repository vai saber qual tabela manipular
    #construtor que recebe o modelo que vai operar
    def __init__(self, model: Type[ModelT]): #construtor recebe o modelo que vai operar 
        self.model = model

    #=============== CRUD ===============
    #método pra buscar um registro pelo id
    def get(self, session: Session, id: Any) -> Optional[ModelT]:
        return session.get(self.model, id)

    #------------------------------------
    #método pra listar todos os registros, com paginação (offset e limit)
    def list(self, session: Session, offset: int = 0, limit: int = 100) -> List[ModelT]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(session.exec(stmt))

    #------------------------------------
    #método pra criar um novo registro   
    def create(self, session: Session, data: CreateT) -> ModelT:
        obj = self.model.model_validate(data)  # converte CreateT -> ModelT
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    #------------------------------------
    #método pra atualizar um registro
    def update(self, session: Session, obj: ModelT, data: UpdateT) -> ModelT:
        data_dict = data.model_dump(exclude_unset=True)
        for k, v in data_dict.items():
            setattr(obj, k, v)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    #------------------------------------
    #método pra deletar um registro
    def delete(self, session: Session, obj: ModelT) -> None:
        session.delete(obj)
        session.commit()
