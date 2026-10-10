CREATE TABLE item_estoque (
    codigo_prod INTEGER NOT NULL,
    codigo_deposito SMALLINT NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    data_ultima_conferencia DATE,
    CONSTRAINT pk_item_estoque PRIMARY KEY (codigo_prod, codigo_deposito)
);
\dt
\d item_estoque
