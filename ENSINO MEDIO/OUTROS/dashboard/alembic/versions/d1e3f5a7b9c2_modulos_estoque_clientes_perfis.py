"""adiciona estoque, clientes e perfis

Revision ID: d1e3f5a7b9c2
Revises: 954ce858cd0e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1e3f5a7b9c2"
down_revision: Union[str, Sequence[str], None] = "954ce858cd0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("cpf_cnpj", sa.String(length=14), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("telefone", sa.String(length=30), nullable=True),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf_cnpj"),
    )
    op.create_index(op.f("ix_clientes_id"), "clientes", ["id"], unique=False)
    op.create_index(op.f("ix_clientes_nome"), "clientes", ["nome"], unique=False)
    op.create_index(op.f("ix_clientes_cpf_cnpj"), "clientes", ["cpf_cnpj"], unique=False)
    op.add_column("usuarios", sa.Column("perfil", sa.String(length=20), nullable=False, server_default="ADMIN"))
    op.alter_column("usuarios", "perfil", server_default=None)
    op.add_column("vendas", sa.Column("cliente_id", sa.Integer(), nullable=True))
    op.add_column("vendas", sa.Column("status", sa.String(length=20), nullable=False, server_default="CONCLUIDA"))
    op.alter_column("vendas", "status", server_default=None)
    op.add_column("vendas", sa.Column("data_cancelamento", sa.DateTime(), nullable=True))
    op.add_column("vendas", sa.Column("motivo_cancelamento", sa.String(length=255), nullable=True))
    op.create_foreign_key("fk_vendas_cliente_id", "vendas", "clientes", ["cliente_id"], ["id"])
    op.create_table(
        "movimentacoes_estoque",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("origem", sa.String(length=50), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.Column("venda_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["venda_id"], ["vendas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for coluna in ("id", "produto_id", "tipo", "venda_id"):
        op.create_index(op.f(f"ix_movimentacoes_estoque_{coluna}"), "movimentacoes_estoque", [coluna], unique=False)
    op.create_table(
        "reservas_estoque",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("origem", sa.String(length=50), nullable=False),
        sa.Column("venda_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["venda_id"], ["vendas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for coluna in ("id", "produto_id", "status", "venda_id"):
        op.create_index(op.f(f"ix_reservas_estoque_{coluna}"), "reservas_estoque", [coluna], unique=False)


def downgrade() -> None:
    op.drop_table("reservas_estoque")
    op.drop_table("movimentacoes_estoque")
    op.drop_constraint("fk_vendas_cliente_id", "vendas", type_="foreignkey")
    op.drop_column("vendas", "motivo_cancelamento")
    op.drop_column("vendas", "data_cancelamento")
    op.drop_column("vendas", "status")
    op.drop_column("vendas", "cliente_id")
    op.drop_column("usuarios", "perfil")
    op.drop_table("clientes")
