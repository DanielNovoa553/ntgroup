import os
import re
from flask import Flask, request, jsonify
import jwt
from utils.utils import *
from db_conexion.db_data import connectdb
from datetime import datetime, date, timezone, timedelta

app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
app.config['SECRET_KEY'] = secret_key


def generate_token():
    try:
        time = datetime.now(tz=timezone.utc)
        plus_time = timedelta(minutes=60)
        expiration_time_mexico = datetime.now() + plus_time
        expiration_time = time + plus_time

        payload = {
            'exp': expiration_time,
            'iat': time
        }

        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token, expiration_time_mexico

    except Exception as e:
        raise Exception(f"Error al generar el token: {str(e)}")


def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token a expirado.',
                'status': False}
    except jwt.InvalidTokenError:
        return {'error': 'Token Invalido.'}


# Endpoint para obtener un token de acceso y hacer login
@app.route("/api/login", methods=["GET"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos.'})

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Usuario o contraseña no proporcionados.'})

        conn = connectdb()
        cursor = conn.cursor()
        sql = f"SELECT * FROM usuario WHERE email = '{email}' AND password = '{password}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            token = generate_token()
            expiration_time_mexico = token[1].strftime("%d-%m-%Y %H:%M:%S")
            conn.close()
            cursor.close()
            return jsonify({'token': token[0],
                            'status': 'Inicio de sesión exitoso.',
                            'message': 'Token generado exitosamente.',
                            'expiration_time': expiration_time_mexico,
                            'email': email})
        else:
            conn.close()
            cursor.close()
            return jsonify({'error': 'Credenciales invalidas.'})

    except Exception as e:
        return jsonify({"error": f"Error al registrar el usuario: {str(e)}"}), 500


# Endpoint para registrar un usuario
@app.route("/api/register", methods=["POST"])
def register_user():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({"error": "Token no proporcionado."}), 400

        payload = verify_token(token)
        if 'error' in payload:
            return jsonify(payload), 400


        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos."}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Los campos 'email' y 'password' son obligatorios."}), 400

        # Validar email
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "El email no tiene un formato válido."}), 400

        if validate_email(email):
            return jsonify({"error": "El email ya está registrado."}), 400

        # Validar contraseña
        if not password or not validate_password(password):
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres."}), 400

        hash_password = covert_password(password)

        # Insertar el usuario en la base de datos
        conn = connectdb()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuario (email, password) VALUES (%s, %s)", (email, hash_password))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Usuario registrado exitosamente."}), 201

    except Exception as e:
        return jsonify({"error": f"Error al registrar el usuario: {str(e)}"}), 500


@app.route("/api/gastos-diarios", methods=["GET"])
def get_gastos_diarios():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({"error": "Token no proporcionado."}), 400

        payload = verify_token(token)
        if 'error' in payload:
            return jsonify(payload), 400

        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")

        condiciones = []
        parametros = []

        if fecha_inicio:
            try:
                datetime.strptime(fecha_inicio, "%d-%m-%Y")
                condiciones.append("fecha_pago >= %s")
                parametros.append(fecha_inicio)
            except ValueError:
                return jsonify({"error": "fecha_inicio no tiene formato valido (DD-MM-YYYY)"}), 400

        if fecha_fin:
            try:
                datetime.strptime(fecha_fin, "%d-%m-%Y")
                condiciones.append("fecha_pago <= %s")
                parametros.append(fecha_fin)
            except ValueError:
                return jsonify({"error": "fecha_fin no tiene formato valido (DD-MM-YYYY)"}), 400

        query = "SELECT * FROM transacciones_diarias"
        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)
        query += " ORDER BY fecha_pago ASC"

        conn = connectdb()
        cur = conn.cursor()
        cur.execute(query, tuple(parametros))
        rows = cur.fetchall()

        if not rows:
            return jsonify({"error": "No hay datos disponibles para el rango de fechas solicitado."}), 404

        colnames = [desc[0] for desc in cur.description]
        resultados = []

        # Diccionario para renombrar columnas
        renombrar_columnas = {
            "company_id": "id_empresa",
            "company_name": "nombre_empresa",
            "fecha_pago": "fecha",
            "monto_total": "monto_diario"
        }

        for row in rows:
            row_dict = dict(zip(colnames, row))
            if "fecha_pago" in row_dict and isinstance(row_dict["fecha_pago"], (datetime, date)):
                row_dict["fecha_pago"] = row_dict["fecha_pago"].strftime("%d/%m/%Y")

            # Renombrar columnas
            row_dict_renombrado = {renombrar_columnas.get(k, k): v for k, v in row_dict.items()}
            resultados.append(row_dict_renombrado)

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Transacciones del dia obtenidas con exito",
            "transacciones_diarias": resultados
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error al consultar la vista: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)


