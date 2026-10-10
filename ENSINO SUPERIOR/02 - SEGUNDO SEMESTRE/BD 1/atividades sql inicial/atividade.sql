-- Banco de Dados I | Atividades - SQL - Inicial
-- Execução: psql -X -v ON_ERROR_STOP=1 -d postgres -f atividade.sql
-- Execute em uma instância em que loja_vendas e loja_estoque não existam.
-- Meta-comandos do psql não recebem ponto e vírgula.

\set ON_ERROR_STOP on
\pset pager off

-- ETAPA 01: Exercício 1 - criar e verificar o banco loja_vendas
CREATE DATABASE loja_vendas;
\l
\c loja_vendas

-- ETAPA 02: Exercício 1 - criar e verificar produto
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

-- ETAPA 03: Exercício 2 - criar e verificar vendedor
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

-- ETAPA 04: Exercício 3 - criar e verificar o banco loja_estoque
CREATE DATABASE loja_estoque;
\l
\c loja_estoque

-- ETAPA 05: Exercício 3 - criar e verificar fornecedor
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

-- ETAPA 06: Exercício 4 - criar e verificar item_estoque
CREATE TABLE item_estoque (
    codigo_prod INTEGER NOT NULL,
    codigo_deposito SMALLINT NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    data_ultima_conferencia DATE,
    CONSTRAINT pk_item_estoque PRIMARY KEY (codigo_prod, codigo_deposito)
);
\dt
\d item_estoque
