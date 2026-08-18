from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    ordem = db.Column(db.Integer, default=0)

    produtos = db.relationship(
        "Produto", backref="categoria", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Categoria {self.nome}>"


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    imagem_url = db.Column(db.String(300), nullable=True)
    disponivel = db.Column(db.Boolean, default=True)
    destaque = db.Column(db.Boolean, default=False)

    # campos extras usados nos cards de sabor da VITTA
    tag = db.Column(db.String(60), nullable=True)          # ex: "o original"
    ingredientes = db.Column(db.Text, nullable=True)
    alergenos = db.Column(db.Text, nullable=True)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def preco_formatado(self):
        return f"R$ {self.preco:.2f}".replace(".", ",")

    def __repr__(self):
        return f"<Produto {self.nome}>"


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    detalhes = db.Column(db.Text, nullable=False)
    data_desejada = db.Column(db.String(60), nullable=True)
    status = db.Column(db.String(20), default="novo")  # novo, em_andamento, concluido, cancelado
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Pedido {self.id} - {self.nome_cliente}>"
