import os
import urllib.parse

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from config import Config
from models import db, Admin, Categoria, Produto, Pedido

# cahio esteve aqui

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # garante que a pasta instance/ existe (onde fica o vitta.db do SQLite)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "admin_login"
    login_manager.login_message = "Faça login para acessar o painel administrativo."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    # -------------------- injeta dados da empresa em todos os templates --------------------
    @app.context_processor
    def dados_empresa():
        return dict(
            nome_empresa=app.config["NOME_EMPRESA"],
            slogan=app.config["SLOGAN"],
            whatsapp=app.config["WHATSAPP"],
            instagram=app.config["INSTAGRAM"],
            email_contato=app.config["EMAIL_CONTATO"],
            endereco=app.config["ENDERECO"],
        )

    # ==================================================================
    # PÁGINAS PÚBLICAS
    # ==================================================================
    @app.route("/")
    def index():
        destaques = (
            Produto.query.filter_by(disponivel=True, destaque=True)
            .order_by(Produto.criado_em.desc())
            .limit(3)
            .all()
        )
        return render_template("index.html", destaques=destaques)

    @app.route("/sobre")
    def sobre():
        return render_template("sobre.html")

    @app.route("/cardapio")
    def cardapio():
        categorias = Categoria.query.order_by(Categoria.ordem, Categoria.nome).all()
        # produtos sem categoria também aparecem, num grupo à parte
        sem_categoria = (
            Produto.query.filter_by(categoria_id=None, disponivel=True)
            .order_by(Produto.nome)
            .all()
        )
        return render_template("cardapio.html", categorias=categorias, sem_categoria=sem_categoria)

    @app.route("/pedido-rapido", methods=["POST"])
    def pedido_rapido():
        """Botão 'Pedir' de cada sabor: manda direto pro WhatsApp já com a mensagem escrita."""
        produto_id = request.form.get("produto_id", "")
        produto = db.session.get(Produto, int(produto_id)) if produto_id.isdigit() else None

        if produto:
            msg = f"Oioi, gostaria de adoçar meu dia com um pedido :) Quero o brownie de *{produto.nome}* ({produto.preco_formatado()})."
        else:
            msg = "Oioi, gostaria de adoçar meu dia com um pedido :)"

        url = f"https://wa.me/{Config.WHATSAPP}?text={urllib.parse.quote(msg)}"
        return redirect(url)

    @app.route("/contato", methods=["GET", "POST"])
    def contato():
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            telefone = request.form.get("telefone", "").strip()
            email = request.form.get("email", "").strip()
            detalhes = request.form.get("detalhes", "").strip()
            data_desejada = request.form.get("data_desejada", "").strip()

            erros = []
            if not nome:
                erros.append("Informe seu nome.")
            if not telefone:
                erros.append("Informe um telefone para contato.")
            if not detalhes:
                erros.append("Descreva o que você gostaria de encomendar.")

            if erros:
                for e in erros:
                    flash(e, "erro")
                return render_template(
                    "contato.html",
                    nome=nome, telefone=telefone, email=email,
                    detalhes=detalhes, data_desejada=data_desejada,
                )

            pedido = Pedido(
                nome_cliente=nome,
                telefone=telefone,
                email=email or None,
                detalhes=detalhes,
                data_desejada=data_desejada or None,
            )
            db.session.add(pedido)
            db.session.commit()

            flash("Pedido enviado com sucesso! Em breve entraremos em contato para confirmar.", "sucesso")
            return redirect(url_for("contato"))

        return render_template("contato.html")

    # ==================================================================
    # ÁREA ADMINISTRATIVA
    # ==================================================================
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            usuario = request.form.get("usuario", "").strip()
            senha = request.form.get("senha", "")
            admin = Admin.query.filter_by(usuario=usuario).first()

            if admin and admin.checar_senha(senha):
                login_user(admin)
                return redirect(url_for("admin_dashboard"))

            flash("Usuário ou senha inválidos.", "erro")

        return render_template("admin/login.html")

    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for("admin_login"))

    @app.route("/admin")
    @login_required
    def admin_dashboard():
        total_pedidos_novos = Pedido.query.filter_by(status="novo").count()
        total_produtos = Produto.query.count()
        ultimos_pedidos = Pedido.query.order_by(Pedido.criado_em.desc()).limit(5).all()
        return render_template(
            "admin/dashboard.html",
            total_pedidos_novos=total_pedidos_novos,
            total_produtos=total_produtos,
            ultimos_pedidos=ultimos_pedidos,
        )

    # -------------------- pedidos --------------------
    @app.route("/admin/pedidos")
    @login_required
    def admin_pedidos():
        filtro = request.args.get("status", "todos")
        query = Pedido.query
        if filtro != "todos":
            query = query.filter_by(status=filtro)
        pedidos = query.order_by(Pedido.criado_em.desc()).all()
        return render_template("admin/pedidos.html", pedidos=pedidos, filtro=filtro)

    @app.route("/admin/pedidos/<int:pedido_id>/status", methods=["POST"])
    @login_required
    def admin_pedido_status(pedido_id):
        pedido = db.session.get(Pedido, pedido_id) or abort(404)
        novo_status = request.form.get("status")
        if novo_status in ("novo", "em_andamento", "concluido", "cancelado"):
            pedido.status = novo_status
            db.session.commit()
            flash("Status do pedido atualizado.", "sucesso")
        return redirect(url_for("admin_pedidos"))

    @app.route("/admin/pedidos/<int:pedido_id>/excluir", methods=["POST"])
    @login_required
    def admin_pedido_excluir(pedido_id):
        pedido = db.session.get(Pedido, pedido_id) or abort(404)
        db.session.delete(pedido)
        db.session.commit()
        flash("Pedido excluído.", "sucesso")
        return redirect(url_for("admin_pedidos"))

    # -------------------- produtos (cardápio) --------------------
    @app.route("/admin/produtos")
    @login_required
    def admin_produtos():
        produtos = Produto.query.order_by(Produto.nome).all()
        return render_template("admin/produtos.html", produtos=produtos)

    @app.route("/admin/produtos/novo", methods=["GET", "POST"])
    @login_required
    def admin_produto_novo():
        categorias = Categoria.query.order_by(Categoria.nome).all()
        if request.method == "POST":
            produto = Produto(
                nome=request.form.get("nome", "").strip(),
                descricao=request.form.get("descricao", "").strip(),
                preco=request.form.get("preco", "0").replace(",", "."),
                tag=request.form.get("tag", "").strip() or None,
                ingredientes=request.form.get("ingredientes", "").strip() or None,
                alergenos=request.form.get("alergenos", "").strip() or None,
                imagem_url=request.form.get("imagem_url", "").strip() or None,
                disponivel=bool(request.form.get("disponivel")),
                destaque=bool(request.form.get("destaque")),
                categoria_id=request.form.get("categoria_id") or None,
            )
            db.session.add(produto)
            db.session.commit()
            flash("Produto adicionado ao cardápio.", "sucesso")
            return redirect(url_for("admin_produtos"))

        return render_template("admin/produto_form.html", produto=None, categorias=categorias)

    @app.route("/admin/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
    @login_required
    def admin_produto_editar(produto_id):
        produto = db.session.get(Produto, produto_id) or abort(404)
        categorias = Categoria.query.order_by(Categoria.nome).all()

        if request.method == "POST":
            produto.nome = request.form.get("nome", "").strip()
            produto.descricao = request.form.get("descricao", "").strip()
            produto.preco = request.form.get("preco", "0").replace(",", ".")
            produto.tag = request.form.get("tag", "").strip() or None
            produto.ingredientes = request.form.get("ingredientes", "").strip() or None
            produto.alergenos = request.form.get("alergenos", "").strip() or None
            produto.imagem_url = request.form.get("imagem_url", "").strip() or None
            produto.disponivel = bool(request.form.get("disponivel"))
            produto.destaque = bool(request.form.get("destaque"))
            produto.categoria_id = request.form.get("categoria_id") or None
            db.session.commit()
            flash("Produto atualizado.", "sucesso")
            return redirect(url_for("admin_produtos"))

        return render_template("admin/produto_form.html", produto=produto, categorias=categorias)

    @app.route("/admin/produtos/<int:produto_id>/excluir", methods=["POST"])
    @login_required
    def admin_produto_excluir(produto_id):
        produto = db.session.get(Produto, produto_id) or abort(404)
        db.session.delete(produto)
        db.session.commit()
        flash("Produto removido do cardápio.", "sucesso")
        return redirect(url_for("admin_produtos"))

    # -------------------- categorias --------------------
    @app.route("/admin/categorias", methods=["GET", "POST"])
    @login_required
    def admin_categorias():
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            if nome:
                db.session.add(Categoria(nome=nome))
                db.session.commit()
                flash("Categoria criada.", "sucesso")
            return redirect(url_for("admin_categorias"))

        categorias = Categoria.query.order_by(Categoria.ordem, Categoria.nome).all()
        return render_template("admin/categorias.html", categorias=categorias)

    @app.route("/admin/categorias/<int:categoria_id>/excluir", methods=["POST"])
    @login_required
    def admin_categoria_excluir(categoria_id):
        categoria = db.session.get(Categoria, categoria_id) or abort(404)
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoria removida (produtos dela ficaram sem categoria).", "sucesso")
        return redirect(url_for("admin_categorias"))

    # ==================================================================
    # COMANDOS DE LINHA DE COMANDO (setup do banco)
    # ==================================================================
    @app.cli.command("init-db")
    def init_db():
        """Cria as tabelas do banco de dados."""
        db.create_all()
        print("Banco de dados criado com sucesso.")

    @app.cli.command("create-admin")
    def create_admin():
        """Cria um usuário administrador (usuario: admin / senha: admin123)."""
        if Admin.query.filter_by(usuario="admin").first():
            print("Usuário admin já existe.")
            return
        admin = Admin(usuario="admin")
        admin.set_senha("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin criado! usuário: admin | senha: admin123")
        print("IMPORTANTE: troque essa senha depois de logar pela primeira vez.")

    @app.cli.command("seed-db")
    def seed_db():
        """Popula o cardápio inicial da VITTA (só roda se estiver vazio)."""
        if Produto.query.count() > 0:
            print("Já existem produtos cadastrados — nada foi alterado.")
            return

        cat_classicos = Categoria(nome="Sabores", ordem=1)
        db.session.add(cat_classicos)
        db.session.flush()

        produtos = [
            Produto(
                nome="Brownie de Brigadeiro",
                descricao="Brownie fudgy de cacau com recheio cremoso de brigadeiro e granulado de chocolate.",
                preco=8.50, tag="clássico", destaque=True,
                ingredientes="Cacau, brigadeiro cremoso, granulado de chocolate, manteiga, ovos, farinha.",
                alergenos="Contém glúten, ovos e laticínios.",
                categoria=cat_classicos,
            ),
            Produto(
                nome="Brownie de Ninho",
                descricao="Base de brownie tradicional com recheio cremoso de leite Ninho.",
                preco=8.50, tag="queridinho", destaque=True,
                ingredientes="Cacau, creme de leite Ninho, manteiga, ovos, farinha.",
                alergenos="Contém glúten, ovos e laticínios.",
                categoria=cat_classicos,
            ),
        ]
        db.session.add_all(produtos)
        db.session.commit()
        print(f"Cardápio inicial criado: {len(produtos)} produtos em 1 categoria.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
