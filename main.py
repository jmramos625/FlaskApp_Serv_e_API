from flask import Flask  # para importar a classe a abrir a aplicação
from flask import request  # para usar parâmetros
from flask import render_template  # juntar código com a requisição
from flask_sqlalchemy import SQLAlchemy  # importando ferramenta de banco de dados
from flask import redirect, url_for  # usado para fazer redirecionamento de páginas
from flask import jsonify  # que transforma textos e dados em formatos json

app = Flask(__name__)  # instanciando a classe Flask
db = SQLAlchemy(app)  # objeto do banco de dados

# configurações para funcionamento do DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.sqlite3"  # definindo BD "sqlite" e o seu nome "blog"


# caso fosse criar os usuários
# class User(db.Model):
#     # criando os usuários
#     id = db.Column(db.Integer(), primary_key=True)  # vai ser chave primária pq os Usuários são unicos
#     username = db.Column(db.String())
#     password = db.Column()

# criando um model do BD
class Post(db.Model):
    # criando agora as colunas da tabela
    id = db.Column(db.Integer(), primary_key=True)  # vai ser chave primária pq os ID's são unicos de cada post
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())

    # função para transforma a lista do "post" em dicionário para que possa se tornar um json depois
    def to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result


# criando rota do site
@app.route("/")  # nesse caso -- http://127.0.0.1:5000/
def home():  # essa função é dada como view -- lida com requisições e respostas
    # request para pegar o nome e mudar no código usando parâmetro
    # para mudar nome, no URL faça:
    # http://127.0.0.1:5000/?nome="COLOQUE AQUI O NOME DA PESSOA"
    # nome = request.args.get("nome")

    # pegando todas as postagens para mandar para o render template
    posts = Post.query.all()

    # no return você pode colocar código HTML para ser exibido no site
    # return f"<h1> Fala {nome} seu LINDO</h1>"

    # então ao invés de passar a resposta diretamente no return, vamos usar o render_template para fazer isso
    # com ele vamos criar um arquivo de index.html e definir o que pode ser passado de parâmetro
    # no projeto crie a pasta templates, que é onde ele irá buscar os arquivos
    # com isso não é possível executar alguns códigos na URL
    return render_template("index.html", posts=posts)
    # render template lida com o conteúdo das respostas


# criando lugar onde ficará os posts
# precisamos também adicionar quais métodos iremos aceitar também na requisição
@app.route("/post/add", methods=["POST"])
def add_post():  # adicionando no banco de dados
    try:
        # criando objeto que será inserido no BD
        form = request.form  # quando se cria um formulário, os dados ficam em request.form
        post = Post(title=form["title"], content=form["content"],
                    author=form["author"])  # instancia o objeto da classe Post
        # salvando dentro do banco de dados
        db.session.add(post)
        db.session.commit()  # confirmar a inclusão no banco de dados
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    # redirecionando para a página inicial
    return redirect(url_for("home"))


# deletando um post
# defina o ID do post que será deletado
@app.route("/post/<id>/del")
def delete_post(id):  # adicionando no banco de dados
    try:
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()  # confirmar a exclusão no banco de dados
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    # redirecionando para a página inicial
    return redirect(url_for("home"))


# rota para editar os posts
@app.route("/post/<id>/edit", methods=["POST", "GET"])
def edit_post(id):  # adicionando no banco de dados
    # verificar qual tipo de método é, para determinar uma ação
    if request.method == "POST":
        try:
            # pegando o ID do post que será editado
            post = Post.query.get(id)
            form = request.form
            post.title = form["title"]
            post.content = form["content"]
            post.author = form["author"]
            db.session.commit()  # confirmar a edição no banco de dados
        except Exception as e:
            print(f"ERRO:{e}\n. Revise o código")

        # redirecionando para a página inicial
        return redirect(url_for("home"))
    else:
        try:
            post = Post.query.get(id)
            return render_template("edit.html", post=post)
        except Exception as e:
            print(f"ERRO:{e}\n. Revise o código")

    # caso dê errado, volta para  página HOME
    return redirect(url_for("home"))


# ___________________________________________________________________________________________________
#                                           FORMATO API
# ___________________________________________________________________________________________________


@app.route("/api/posts")
def api_list_posts():
    try:
        posts = Post.query.all()
        # como o objeto posts vem como lista, não teria como colocar diretamente em json pois ele usa dicionários
        # para isso usamos uma fórmula chama .to_dict que transforma em dicionário e com isso pode-se converte em json
        return jsonify([post.to_dic() for post in posts])
        # com isso transforma em json cada post que está nele
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    return jsonify([])


@app.route("/api/post", methods=["PUT"])
def api_add_post():  # adicionando no banco de dados
    try:
        # nesse caso vamos pegar a requisição e já jogá-la dentro do banco de dados
        data = request.get_json()
        post = Post(title=data["title"], content=data["content"],
                    author=data["author"])  # instancia o objeto da classe Post
        # salvando dentro do banco de dados
        db.session.add(post)
        db.session.commit()  # confirmar a inclusão no banco de dados
        return jsonify({"success": True})
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    # EX para enviar de requisição como JSON: {"title": "TITULO API", "content": "conteudo", "author": "API REST JOAO"}

    # nesse caso como é uma API eu preciso retonar um JSON
    return jsonify({"success": False})


@app.route("/api/post/<id>", methods=["DELETE"])
def api_delete_post(id):
    try:
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()  # confirmar a exclusão no banco de dados
        return jsonify({"success": True})
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    # redirecionando para a página inicial
    return jsonify({"success": False})


@app.route("/api/post/<id>", methods=["PUT"])
def api_edit_post(id):  # adicionando no banco de dados
    try:
        # pegando o ID do post que será editado
        post = Post.query.get(id)
        data = request.get_json()
        post.title = data["title"]
        post.content = data["content"]
        post.author = data["author"]
        db.session.commit()  # confirmar a edição no banco de dados
        return jsonify({"success": True})
    except Exception as e:
        print(f"ERRO:{e}\n. Revise o código")

    return jsonify({"success": False})


# ___________________________________________________________________________________________________
#                                                PROTEÇÕES
# ___________________________________________________________________________________________________

# função usada para proteger o site contra a criação de um iframe
# <iframe src"127.0.0.1:5000">
@app.after_request
def add_header(response):
    response.headers["X-Frame-Options"] = "DENY"  # define que nenhum site consiga criar um iframe do mesmo
    response.headers["Content-Security-Policy"] = "script-src 'none'"  # nenhum script pode ser executado
    # se no lugar de 'none' estiver 'unsafe-inline' os códigos poderão se executados
    response.headers["Access-Control-Allow-Origin"] = "*"  # permite acessar meu site de qualquer dominio
    response.headers["Access-Control-Allow-Credentials"] = "true"  # além de qualquer dominio, ainda usar credenciais
    return response


# ___________________________________________________________________________________________________
#                         CRIAÇÃO DO BANCO DE DADOS E EXECUÇÃO DA APLICAÇÃO
# ___________________________________________________________________________________________________

# usado para criar o banco de dados conforme feito na classe POST
db.create_all()

app.run(debug=True)  # rodando a aplicação, com isso o servidor Flask, já está em funcionamento
# roda na maioria das vezes em "http://127.0.0.1:5000"
# debug=True, define que as modificações que ficar no código, serão feitas em tempo real no site
