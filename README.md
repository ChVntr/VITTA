# VITTA — site em Flask (com banco de dados e painel administrativo)

Site do projeto de itinerário, marca de brownies **VITTA** (do latim *vita*, vida).

Esta versão segue a estrutura ensinada na apostila da escola: banco de dados com
Flask-SQLAlchemy, login administrativo com Flask-Login, e um painel para gerenciar
pedidos, produtos e categorias sem precisar mexer no código.

## Como rodar

```bash
pip install -r requirements.txt

# cria o banco de dados (arquivo instance/vitta.db)
flask --app app init-db

# cria o usuário administrador (usuário: admin / senha: admin123)
flask --app app create-admin

# carrega o cardápio inicial da VITTA (5 sabores, 2 categorias)
flask --app app seed-db

# roda o site
flask --app app run --debug
```

Abra **http://127.0.0.1:5000** para o site público.

Abra **http://127.0.0.1:5000/admin/login** para o painel administrativo
(usuário `admin`, senha `admin123` — troque assim que possível).

## O que dá pra fazer pelo painel admin

- **Pedidos**: ver encomendas enviadas pelo formulário de contato, filtrar por
  status (novo / em andamento / concluído / cancelado) e marcar como resolvido.
- **Cardápio**: adicionar, editar e remover sabores — nome, descrição, preço,
  ingredientes, alérgenos, categoria, se está disponível e se aparece em destaque
  na home.
- **Categorias**: criar e remover categorias do cardápio.

## Estrutura do projeto

```
vitta/
├── app.py              → rotas públicas + painel admin (application factory)
├── config.py            → nome da marca, slogan, contatos, banco de dados
├── models.py             → tabelas do banco: Admin, Categoria, Produto, Pedido
├── requirements.txt
├── templates/
│   ├── base.html         → molde do site público
│   ├── index.html, sobre.html, cardapio.html, contato.html
│   └── admin/             → painel administrativo (login, dashboard, pedidos, cardápio, categorias)
└── static/
    ├── css/style.css      → aparência do site público
    ├── css/admin.css      → aparência do painel admin
    ├── js/main.js          → menu mobile
    └── img/                → logo (SVG e PNG) e favicon
```

## O que editar

- **Nome, slogan, WhatsApp, Instagram, e-mail** → `config.py`
- **Sabores e categorias** → pelo painel admin (`/admin/produtos`, `/admin/categorias`),
  ou direto no banco pelo comando `flask --app app seed-db` (edite a lista dentro de `app.py`)
- **Cores e fontes** → `static/css/style.css`, bloco `:root` no topo

## Paleta usada

| Nome | Hex |
|---|---|
| Cosmic Latte (fundo) | `#FFF8E7` |
| Butter (seções claras) | `#FFF0C8` |
| Juicy Orange (destaque) | `#F67D2C` |
| Cacau (texto/rodapé/admin) | `#3B2417` |

## Resolvendo problemas comuns

- **"comando não encontrado" ao digitar flask** → o ambiente virtual não está
  ativado, ou as bibliotecas do `requirements.txt` não foram instaladas.
- **Página em branco ou erro 500** → leia a mensagem no terminal, ela aponta o
  arquivo e a linha exata do problema.
- **Cardápio vazio no site** → rode `flask --app app seed-db` para carregar os
  5 sabores iniciais.
- **Banco de dados com erro estranho** → apague o arquivo `instance/vitta.db`
  e rode `flask --app app init-db` de novo (isso apaga os dados, cuidado).

## Arquivo `preview.html`

Versão estática (sem Flask, sem banco de dados) só para visualizar o design
rapidinho no navegador, sem precisar instalar nada.
