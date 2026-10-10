from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ClienteBase(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
    endereco: str | None = Field(default=None, max_length=255)

    @field_validator("cpf_cnpj")
    @classmethod
    def normalizar_documento(cls, valor: str | None) -> str | None:
        if not valor:
            return None
        documento = "".join(caractere for caractere in valor if caractere.isdigit())
        if len(documento) not in {11, 14}:
            raise ValueError("CPF/CNPJ deve conter 11 ou 14 digitos")
        return documento


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
    endereco: str | None = Field(default=None, max_length=255)

    @field_validator("cpf_cnpj")
    @classmethod
    def normalizar_documento(cls, valor: str | None) -> str | None:
        return ClienteBase.normalizar_documento(valor)


class ClienteOut(ClienteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
