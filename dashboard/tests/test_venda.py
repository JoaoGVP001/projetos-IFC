from decimal import Decimal

import pytest

from app.crud.venda import (
    EstoqueInsuficienteError,
    ProdutoNaoEncontradoError,
    criar_venda,
)
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.venda import Venda
from app.schemas.venda import ItemVendaCreate, VendaCreate


def criar_usuario(db) -> Usuario:
    usuario = Usuario(
        username="operador",
        email="operador@example.com",
        senha_hash="hash-de-teste",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def criar_produto(db, nome: str, preco: str, estoque: int) -> Produto:
    produto = Produto(
        nome=nome,
        preco=Decimal(preco),
        quantidade_estoque=estoque,
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def test_criar_venda_calcula_total_e_baixa_estoque(db):
    usuario = criar_usuario(db)
    produto = criar_produto(db, "Teclado", "120.00", 5)

    venda = criar_venda(
        db,
        usuario.id,
        VendaCreate(itens=[ItemVendaCreate(produto_id=produto.id, quantidade=2)]),
    )

    db.refresh(produto)
    assert venda.valor_total == Decimal("240.00")
    assert produto.quantidade_estoque == 3
    assert venda.itens[0].preco_unitario == Decimal("120.00")


def test_criar_venda_consolida_produto_repetido(db):
    usuario = criar_usuario(db)
    produto = criar_produto(db, "Mouse", "50.00", 5)

    venda = criar_venda(
        db,
        usuario.id,
        VendaCreate(
            itens=[
                ItemVendaCreate(produto_id=produto.id, quantidade=2),
                ItemVendaCreate(produto_id=produto.id, quantidade=3),
            ]
        ),
    )

    db.refresh(produto)
    assert produto.quantidade_estoque == 0
    assert venda.valor_total == Decimal("250.00")
    assert len(venda.itens) == 1
    assert venda.itens[0].quantidade == 5


def test_criar_venda_com_estoque_insuficiente_nao_altera_produtos(db):
    usuario = criar_usuario(db)
    produto_disponivel = criar_produto(db, "Monitor", "900.00", 2)
    produto_indisponivel = criar_produto(db, "Cabo", "20.00", 1)

    with pytest.raises(EstoqueInsuficienteError):
        criar_venda(
            db,
            usuario.id,
            VendaCreate(
                itens=[
                    ItemVendaCreate(produto_id=produto_disponivel.id, quantidade=1),
                    ItemVendaCreate(produto_id=produto_indisponivel.id, quantidade=2),
                ]
            ),
        )

    db.refresh(produto_disponivel)
    db.refresh(produto_indisponivel)
    assert produto_disponivel.quantidade_estoque == 2
    assert produto_indisponivel.quantidade_estoque == 1
    assert db.query(Venda).count() == 0


def test_criar_venda_rejeita_produto_inexistente(db):
    usuario = criar_usuario(db)

    with pytest.raises(ProdutoNaoEncontradoError):
        criar_venda(
            db,
            usuario.id,
            VendaCreate(itens=[ItemVendaCreate(produto_id=999, quantidade=1)]),
        )
