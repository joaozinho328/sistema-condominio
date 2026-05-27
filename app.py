from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "condominio"

# CONEXAO MYSQL
def conectar():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="condominio"
    )

# CRIAR TABELAS
def criar_banco():

    conexao = conectar()

    cursor = conexao.cursor()

    # TABELA USUARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100),
        email VARCHAR(100),
        senha VARCHAR(100),
        tipo VARCHAR(50)
    )
    """)

    # TABELA RESERVAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        area VARCHAR(100),
        data VARCHAR(100),
        horario VARCHAR(100)
    )
    """)

    # TABELA AVISOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avisos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(200),
        mensagem TEXT
    )
    """)

    # TABELA SUGESTOES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sugestoes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        mensagem TEXT
    )
    """)

    # TABELA MENSAGENS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        mensagem TEXT
    )
    """)

    # TABELA PAGAMENTOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        descricao VARCHAR(200),
        valor DECIMAL(10,2),
        status VARCHAR(50)
    )
    """)

    conexao.commit()

    conexao.close()

# PAGINA INICIAL
@app.route("/")
def inicio():

    return redirect("/login")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar()

        cursor = conexao.cursor()

        cursor.execute("""
        SELECT * FROM usuarios
        WHERE email = %s
        AND senha = %s
        """, (email, senha))

        usuario = cursor.fetchone()

        conexao.close()

        if usuario:

            session["usuario"] = usuario[1]
            session["id_usuario"] = usuario[0]
            session["tipo"] = usuario[4]
            session["bloco"] = usuario[5]
            session["apartamento"] = usuario[6]

            return redirect("/painel")

        else:

            return "Email ou senha incorretos!"

    return render_template("login.html")

# CADASTRO
@app.route("/cadastro", methods=["GET", "POST"])
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

# PAINEL
@app.route("/painel")
def painel():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    # TOTAL RESERVAS
    cursor.execute("SELECT COUNT(*) FROM reservas")

    total_reservas = cursor.fetchone()[0]

    # TOTAL AVISOS
    cursor.execute("SELECT COUNT(*) FROM avisos")

    total_avisos = cursor.fetchone()[0]

    # TOTAL SUGESTOES
    cursor.execute("SELECT COUNT(*) FROM sugestoes")

    total_sugestoes = cursor.fetchone()[0]

    # TOTAL MENSAGENS
    cursor.execute("SELECT COUNT(*) FROM mensagens")

    total_mensagens = cursor.fetchone()[0]

    # GRAFICO
    cursor.execute("""
    SELECT area, COUNT(*)
    FROM reservas
    GROUP BY area
    """)

    dados_grafico = cursor.fetchall()

    areas = []
    quantidades = []

    for dado in dados_grafico:

        areas.append(dado[0])

        quantidades.append(dado[1])

    conexao.close()

    return render_template(

        "painel.html",

        total_reservas=total_reservas,

        total_avisos=total_avisos,

        total_sugestoes=total_sugestoes,

        total_mensagens=total_mensagens,

        areas=areas,

        quantidades=quantidades

    )

# RESERVAS
@app.route("/reservas", methods=["GET", "POST"])
def reservas():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == "POST":

        area = request.form["area"]

        data = request.form["data"]

        horario = request.form["horario"]

        cursor.execute("""
        SELECT *
        FROM reservas
        WHERE area = %s
        AND data = %s
        AND horario = %s
        """, (area, data, horario))

        reserva_existente = cursor.fetchone()

        if reserva_existente:

            flash("Horário já reservado!")

            conexao.close()

            return redirect("/reservas")

        cursor.execute("""
        INSERT INTO reservas
        (usuario_id, area, data, horario)

        VALUES (%s, %s, %s, %s)
        """, (
            session["id_usuario"],
            area,
            data,
            horario
        ))

        conexao.commit()

        flash("Reserva realizada com sucesso!")

        conexao.close()

        return redirect("/lista")

    cursor.execute("""
    SELECT area, data, horario
    FROM reservas
    """)

    reservas = cursor.fetchall()

    eventos = []

    for reserva in reservas:

        eventos.append({

            "title": f"{reserva[0]} - {reserva[2]}",

            "start": str(reserva[1])

        })

    conexao.close()

    return render_template(
        "reservas.html",
        eventos=eventos
    )

# LISTA RESERVAS
@app.route("/lista")
def lista():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM reservas
    WHERE usuario_id = %s
    """, (session["id_usuario"],))

    reservas = cursor.fetchall()

    conexao.close()

    return render_template("lista.html", reservas=reservas)

# EXCLUIR
@app.route("/excluir/<int:id>")
def excluir(id):

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    DELETE FROM reservas
    WHERE id = %s
    """, (id,))

    conexao.commit()

    conexao.close()

    return redirect("/lista")

# EDITAR
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == "POST":

        area = request.form["area"]
        data = request.form["data"]
        horario = request.form["horario"]

        cursor.execute("""
        UPDATE reservas
        SET area = %s, data = %s, horario = %s
        WHERE id = %s
        """, (area, data, horario, id))

        conexao.commit()

        conexao.close()

        return redirect("/lista")

    cursor.execute("""
    SELECT * FROM reservas
    WHERE id = %s
    """, (id,))

    reserva = cursor.fetchone()

    conexao.close()

    return render_template("editar.html", reserva=reserva)

# AVISOS
@app.route("/avisos", methods=["GET", "POST"])
def avisos():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == "POST":

        if session["tipo"] != "admin":

            return "Apenas administradores!"

        titulo = request.form["titulo"]
        mensagem = request.form["mensagem"]

        cursor.execute("""
        INSERT INTO avisos (titulo, mensagem)
        VALUES (%s, %s)
        """, (titulo, mensagem))

        conexao.commit()

    cursor.execute("SELECT * FROM avisos")

    avisos = cursor.fetchall()

    conexao.close()

    return render_template("avisos.html", avisos=avisos)

# SUGESTOES
@app.route("/sugestoes", methods=["GET", "POST"])
def sugestoes():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == "POST":

        mensagem = request.form["mensagem"]

        cursor.execute("""
        INSERT INTO sugestoes (usuario_id, mensagem)
        VALUES (%s, %s)
        """, (session["id_usuario"], mensagem))

        conexao.commit()

    cursor.execute("SELECT * FROM sugestoes")

    sugestoes = cursor.fetchall()

    conexao.close()

    return render_template("sugestoes.html", sugestoes=sugestoes)

# CONVIVENCIA
@app.route("/convivencia", methods=["GET", "POST"])
def convivencia():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    if request.method == "POST":

        mensagem = request.form["mensagem"]

        cursor.execute("""
        INSERT INTO mensagens (usuario_id, mensagem)
        VALUES (%s, %s)
        """, (session["id_usuario"], mensagem))

        conexao.commit()

    cursor.execute("""
    SELECT mensagens.id,
           usuarios.nome,
           mensagens.mensagem
    FROM mensagens
    JOIN usuarios
    ON mensagens.usuario_id = usuarios.id
    ORDER BY mensagens.id DESC
    """)

    mensagens = cursor.fetchall()

    conexao.close()

    return render_template(
        "convivencia.html",
        mensagens=mensagens
    )

# PAGAMENTOS
@app.route("/pagamentos")
def pagamentos():

    if "usuario" not in session:

        return redirect("/login")

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM pagamentos
    WHERE usuario_id = %s
    """, (session["id_usuario"],))

    pagamentos = cursor.fetchall()

    conexao.close()

    return render_template(
        "pagamentos.html",
        pagamentos=pagamentos
    )

# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/admin")
def admin():

    if "usuario" not in session:

        return redirect("/login")

    if session["tipo"] != "admin":

        return "Apenas administradores!"

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT id, nome, email, bloco, apartamento
    FROM usuarios
    """)

    usuarios = cursor.fetchall()

    conexao.close()

    return render_template(
        "admin.html",
        usuarios=usuarios
    )

@app.route("/excluir_usuario/<int:id>")
def excluir_usuario(id):

    if "usuario" not in session:

        return redirect("/login")

    if session["tipo"] != "admin":

        return "Apenas administradores!"

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
    DELETE FROM usuarios
    WHERE id = %s
    """, (id,))

    conexao.commit()

    conexao.close()

    flash("Usuário removido com sucesso!")

    return redirect("/admin")

@app.route("/criar_pagamento", methods=["GET", "POST"])
def criar_pagamento():

    if "usuario" not in session:

        return redirect("/login")

    if session["tipo"] != "admin":

        return "Apenas administradores!"

    conexao = conectar()

    cursor = conexao.cursor()

    # PEGAR USUARIOS
    cursor.execute("""
    SELECT id, nome
    FROM usuarios
    """)

    usuarios = cursor.fetchall()

    if request.method == "POST":

        usuario_id = request.form["usuario_id"]

        descricao = request.form["descricao"]

        valor = request.form["valor"]

        cursor.execute("""
        INSERT INTO pagamentos
        (usuario_id, descricao, valor, status)

        VALUES (%s, %s, %s, %s)
        """, (
            usuario_id,
            descricao,
            valor,
            "Pendente"
        ))

        conexao.commit()

        flash("Cobrança criada com sucesso!")

        return redirect("/admin")

    conexao.close()

    return render_template(
        "criar_pagamento.html",
        usuarios=usuarios
    )

# CRIAR TABELAS
criar_banco()

# RODAR FLASK
if __name__ == "__main__":
    app.run(debug=True)