import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Troque essa chave antes de colocar o site no ar (pode gerar uma nova com:
    # python -c "import secrets; print(secrets.token_hex(32))")
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

    # Por padrão usa SQLite (arquivo local, não precisa instalar nada).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'vitta.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dados institucionais - pode editar aqui ou depois pelo painel admin
    NOME_EMPRESA = os.environ.get("NOME_EMPRESA", "VITTA")
    SLOGAN = os.environ.get("SLOGAN", "vida em cada mordida")
    WHATSAPP = os.environ.get("WHATSAPP", "5521984491546")
    INSTAGRAM = os.environ.get("INSTAGRAM", "vittaabella")
    EMAIL_CONTATO = os.environ.get("EMAIL_CONTATO", "contato@vitta.com.br")
    ENDERECO = os.environ.get("ENDERECO", "Entrega e retirada combinadas por WhatsApp")
