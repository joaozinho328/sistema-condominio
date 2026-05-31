from flask import (
    Blueprint,
    render_template,
    redirect,
    session
)

from database import conectar

admin = Blueprint("admin", __name__)


@admin.route("/admin")
def painel_admin():

    if "usuario" not in session:
        return redirect("/login")

    if session["tipo"] != "admin":
        return "Apenas administradores!"

    conexao = conectar()

    cursor = conexao.cursor()

    # USUÁRIOS
    cursor.execute("""
    SELECT id, nome, email, bloco, apartamento
    FROM usuarios
    """)

    usuarios = cursor.fetchall()

    # TOTAL MORADORES
    cursor.execute("""
    SELECT COUNT(*)
    FROM usuarios
    """)

    total_moradores = cursor.fetchone()[0]

    # TOTAL RESERVAS
    cursor.execute("""
    SELECT COUNT(*)
    FROM reservas
    """)

    total_reservas = cursor.fetchone()[0]

    # PAGAMENTOS PENDENTES
    cursor.execute("""
    SELECT COUNT(*)
    FROM pagamentos
    WHERE status = 'Pendente'
    """)

    pagamentos_pendentes = cursor.fetchone()[0]

    # GRÁFICO
    cursor.execute("""
    SELECT area, COUNT(*)
    FROM reservas
    GROUP BY area
    """)

    dados = cursor.fetchall()

    areas = []
    quantidades = []

    for dado in dados:
        areas.append(dado[0])
        quantidades.append(dado[1])

    conexao.close()

    return render_template(
        "admin.html",
        usuarios=usuarios,
        total_moradores=total_moradores,
        total_reservas=total_reservas,
        pagamentos_pendentes=pagamentos_pendentes,
        areas=areas,
        quantidades=quantidades
    )