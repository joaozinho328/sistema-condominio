from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database import conectar

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar()

        cursor = conexao.cursor()

        cursor.execute("""
        SELECT *
        FROM usuarios
        WHERE email = %s
        AND senha = %s
        """, (email, senha))

        usuario = cursor.fetchone()

        conexao.close()

        if usuario:

            session["usuario"] = usuario[1]
            session["id_usuario"] = usuario[0]
            session["tipo"] = usuario[4]

            # Só usar estas linhas se as colunas
            # bloco e apartamento existirem na tabela
            if len(usuario) > 5:
                session["bloco"] = usuario[5]

            if len(usuario) > 6:
                session["apartamento"] = usuario[6]

            if session["tipo"] == "admin":
                return redirect("/admin")

            return redirect("/painel")

        else:

            return "Email ou senha incorretos!"

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        bloco = request.form["bloco"]
        apartamento = request.form["apartamento"]

        conexao = conectar()

        cursor = conexao.cursor()

        cursor.execute("""
        INSERT INTO usuarios
        (nome, email, senha, tipo, bloco, apartamento)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, email, senha, "morador", bloco, apartamento))

        conexao.commit()

        conexao.close()

        return redirect("/login")

    return render_template("cadastro.html")