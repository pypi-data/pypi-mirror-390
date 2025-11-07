from model.models import EnderecoBase, PessoaBase
from typing import List,Optional
from sqlmodel import Field

class PessoaCreate(PessoaBase):
    pass 

class PessoaPublic(PessoaBase):
    id: int
    model_config = {"from_attributes": True}

class PessoaWithEndereco(PessoaPublic):
    model_config = {"from_attributes": True}
    enderecos: List["EnderecoPublic"] = []

class PessoaUpdate(PessoaBase):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(max_length=120, default=None)

class PessoaRead(PessoaBase):
    id : int

class EnderecoPublic(EnderecoBase):
    id : int
    id_pessoa: Optional[int] = None
    model_config = {"from_attributes": True}

class EnderecoUpdate(EnderecoBase):
    logradouro: Optional[str] = Field(default=None,max_length=120)
    numero: Optional[int] = Field(default=None)
    estado: Optional[str] = Field(default=None,max_length=2, min_length=2)
    cidade: Optional[str] = Field(default=None,max_length=120)
    bairro: Optional[str] = Field(default=None,max_length=120)
    id_pessoa : int

class EnderecoCreate(EnderecoBase):
    id_pessoa: int

class EnderecoRead(EnderecoBase):
    id : int
    id_pessoa : int
    