CREATE TABLE fornecedor (
    cnpj CHAR(14) NOT NULL,
    razao_social VARCHAR(100) NOT NULL,
    nome_fantasia VARCHAR(80),
    telefone VARCHAR(15),
    cidade VARCHAR(60) NOT NULL,
    estado CHAR(2) NOT NULL,
    data_parceria DATE,
    CONSTRAINT pk_fornecedor PRIMARY KEY (cnpj),
    CONSTRAINT unique_razao_social UNIQUE (razao_social)
);
\dt
\d fornecedor

