CREATE TABLE vendedor (
    matricula_vend INTEGER NOT NULL,
    nome_vend VARCHAR(80) NOT NULL,
    cpf CHAR(11) NOT NULL,
    email_vend VARCHAR(80),
    data_admissao DATE NOT NULL,
    comissao_percentual NUMERIC(4, 2) NOT NULL DEFAULT 5.00,
    CONSTRAINT pk_vendedor PRIMARY KEY (matricula_vend),
    CONSTRAINT unique_cpf_vendedor UNIQUE (cpf),
    CONSTRAINT unique_email_vendedor UNIQUE (email_vend)
);
\dt
\d vendedor

