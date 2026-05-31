from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from database import conectar

reservas = Blueprint("reservas", __name__)


@reservas.route("/reservas", methods=["GET", "POST"])
def pagina_reservas():

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

    lista_reservas = cursor.fetchall()

    eventos = []

    for reserva in lista_reservas:

        eventos.append({
            "title": f"{reserva[0]} - {reserva[2]}",
            "start": str(reserva[1])
        })

    conexao.close()

    return render_template(
        "reservas.html",
        eventos=eventos
    )