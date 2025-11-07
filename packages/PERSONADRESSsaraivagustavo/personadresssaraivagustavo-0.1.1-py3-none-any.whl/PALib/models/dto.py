#DTO: é como se fosse um "padrão" para os dados que serão enviados e recebidos pela API, define exatamente quais campos e com quais tipos de dados uma informação deve ser estruturaado para transitar entre cliente e servidor

from .models import EnderecoBase, PessoaBase
from typing import List,Optional
from sqlmodel import Field

#===== DTO para Pessoa =====
class PessoaCreate(PessoaBase):
    pass #pass vai herdar os campos de PessoaBase lá em models.py

class PessoaUpdate(PessoaBase): #todos os campos vão ser opcionais para poder atualizar parcialmente uma pessoa, não sendo necessário enviar todos os campos sempre que for atualizar
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(max_length=120, default=None)

class PessoaRead(PessoaBase): # buscar a pessoa sem os endereços
    id : int

class PessoaReadComEndereco(PessoaRead): # buscar a pessoa com os endereços, é bom separar para não ter que puxar todos os endereços sempre que buscar uma pessoa
    enderecos: List["EnderecoCreate"] = []
    


# ===== DTO para Endereço =====
class EnderecoUpdate(EnderecoBase): #todos os campos vão ser opcionais para poder atualizar parcialmente um endereço, não sendo necessário enviar todos os campos sempre que for atualizar
    logradouro: Optional[str] = Field(default=None,max_length=120)
    numero: Optional[int] = Field(default=None)
    estado: Optional[str] = Field(default=None,max_length=2, min_length=2)
    cidade: Optional[str] = Field(default=None,max_length=120)
    bairro: Optional[str] = Field(default=None,max_length=120)
    id_pessoa : Optional[int] = None

class EnderecoCreate(EnderecoBase):
    id_pessoa: int = Field(foreign_key="pessoa.id") # chave estrangeira obrigatória para criar um endereço, garantindo que todo endereço pertence a uma pessoa

class EnderecoRead(EnderecoBase): #seria o mesmo que EnderecoPublic, só mudei o nome para seguir o CRUD (read)
    id : int
    id_pessoa : Optional[int] = None
    