CREATE TABLE produto (
    codigo_prod INTEGER NOT NULL,
    descricao_prod VARCHAR(100) NOT NULL,
    preco NUMERIC(10, 2) NOT NULL,
    quantidade_estoque SMALLINT NOT NULL DEFAULT 0,
    codigo_barras CHAR(13),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_cadastro DATE,
    CONSTRAINT pk_produto PRIMARY KEY (codigo_prod),
    CONSTRAINT unique_codigo_barras UNIQUE (codigo_barras)
);
\dt
\d produto

