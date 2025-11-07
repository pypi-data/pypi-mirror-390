from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# ===== Modelo para Pessoa =====
# PessoaBase vai definir a base propriamente dita para o modelo Pessoa
class PessoaBase(SQLModel):
    nome: str = Field(min_length=2, max_length=120)
    idade: Optional[int] = Field(default=None, ge=0, le=200)
    email: Optional[str] = Field(max_length=120, unique=True) #email deve ser único porque é um dado sensível

# a classe Pessoa vai representar a tabela no banco de dados, o parâmetro (table=True) faz isso
class Pessoa(PessoaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    enderecos: List["Endereco"] = Relationship(back_populates="pessoa") # uma pessoa pode ter vários endereços, o Relationship do SQLModel faz isso, o parâmetro back_populates cria um relacionamento bidirecional, ou seja, naa classe Endereco também consegue acessar a Pessoa que esse endereço pertence


# ===== Modelo para Endereço =====
# Define a base do modelo Endereco, mesma coisa do PessoaBase
class EnderecoBase(SQLModel):
    logradouro: Optional[str] = Field(max_length=120)
    numero: Optional[int] = Field(default=None)
    estado: Optional[str] = Field(max_length=2, min_length=2)
    cidade: Optional[str] = Field(max_length=120)
    bairro: Optional[str] = Field(max_length=120)

# a classe Endereco vai representar a tabela no banco de dados, o parâmetro (table=True) faz isso
class Endereco(EnderecoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    id_pessoa: Optional[int] = Field(default=None, foreign_key="pessoa.id") # chave estrangeira que referencia a tabela pessoa, no nível de banco, é esse campo garante que um endereço pertence a uma pessoa
    pessoa: Optional[Pessoa] = Relationship(back_populates="enderecos") # aqui é o outro lado do relacionamento criado, ou seja, um endereço pertence a uma pessoa