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
conjunto = ConjuntoNumeros()

def generate_token():
    """
        Genera un token JWT con una expiración de 60 minutos desde el momento actual.

        La función crea un token JWT usando el tiempo actual y lo firma con una clave secreta configurada en `app.config['SECRET_KEY']`.
        El token incluye los siguientes campos en su payload:
        - 'exp': Tiempo de expiración del token (60 minutos después del tiempo actual).
        - 'iat': Tiempo en el que se emite el token (hora actual).

        El token se codifica con el algoritmo HS256 y se devuelve como una cadena de texto. Además, se calcula el tiempo
         de expiración en la zona horaria de México (60 minutos desde la hora actual) y se devuelve junto con el token.

        Returns:
            tuple: Un tuple que contiene:
                - token (str): El token JWT generado.
                - expiration_time_mexico (datetime): La hora de expiración en la zona horaria de México.

        Raises:
            Exception: Si ocurre un error al generar el token, se lanza una excepción con el mensaje de error.
        """
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
    """
        Verifica la validez de un token JWT y decodifica su payload.

        La función intenta decodificar el token JWT proporcionado utilizando la clave secreta configurada en
        `app.config['SECRET_KEY']` y el algoritmo HS256. Si el token es válido, devuelve el payload del token.
        Si el token ha expirado o es inválido, retorna un mensaje de error adecuado.

        Args:
            token (str): El token JWT que se desea verificar.

        Returns:
            dict: Un diccionario con el payload del token si es válido, o un mensaje de error si el token ha expirado
             o es inválido.
                - Si el token es válido: El payload del token.
                - Si el token ha expirado: {'error': 'Token a expirado.', 'status': False}.
                - Si el token es inválido: {'error': 'Token Invalido.'}.

        Raises:
            jwt.ExpiredSignatureError: Si el token ha expirado.
            jwt.InvalidTokenError: Si el token es inválido.
        """
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
    """
        Verifica las credenciales de un usuario y genera un token JWT si son válidas.

        Esta función recibe una solicitud con un correo electrónico y una contraseña, valida que los datos sean
        correctos y, si las credenciales son válidas, genera un token JWT con una expiración de 60 minutos.
        El token se devuelve junto con la hora de expiración y un mensaje de éxito. Si las credenciales son incorrectas,
         devuelve un mensaje de error.

        Args:
            None

        Returns:
            Response: Un objeto JSON con uno de los siguientes resultados:
                - Si las credenciales son correctas:
                    {'token': <token>, 'status': 'Inicio de sesión exitoso.', 'message': 'Token generado exitosamente.',
                     'expiration_time': <expiration_time>, 'email': <email>}
                - Si las credenciales son incorrectas:
                    {'error': 'Credenciales inválidas.'}
                - Si ocurre un error:
                    {'error': 'Error al registrar el usuario: <error_message>'}

        Raises:
            Exception: Si ocurre un error inesperado durante el proceso de autenticación.
        """
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


# Endpoint para obtener gastos diarios por empresa
@app.route("/api/gastos-diarios", methods=["GET"])
def get_gastos_diarios():
    """
        Registra un nuevo usuario en la base de datos.

        Esta función recibe un token de autenticación, verifica su validez, y luego procesa los datos de un nuevo
         usuario (correo electrónico y contraseña). Si los datos son válidos, registra al usuario en la base de datos.
          En caso contrario, devuelve mensajes de error adecuados.

        Args:
            None

        Returns:
            Response: Un objeto JSON con uno de los siguientes resultados:
                - Si el registro es exitoso: {'message': 'Usuario registrado exitosamente.'}
                - Si faltan datos o los datos no son válidos:
                    {'error': 'Token no proporcionado.'}
                    {'error': 'No se proporcionaron datos.'}
                    {'error': 'Los campos "email" y "password" son obligatorios.'}
                    {'error': 'El email no tiene un formato válido.'}
                    {'error': 'El email ya está registrado.'}
                    {'error': 'La contraseña debe tener al menos 8 caracteres.'}
                - Si ocurre un error inesperado: {'error': 'Error al registrar el usuario: <error_message>'}

        Raises:
            Exception: Si ocurre un error inesperado durante el proceso de registro.
        """
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


# endpoint para extraer un número del conjunto
@app.route("/api/extraer_numero", methods=["POST"])
def extraer_numero():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token no proporcionado."}), 400

    payload = verify_token(token)
    if 'error' in payload:
        return jsonify(payload), 400

    data = request.get_json()
    if "numero" not in data:
        return jsonify({"error": "Debes enviar el campo 'numero'"}), 400

    numero = data["numero"]

    try:
        conjunto.extract(numero)
        return jsonify({"mensaje": f"Número {numero} extraído correctamente."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# endpoint para obtener el número faltante del conjunto
@app.route("/api/faltante", methods=["GET"])
def obtener_faltante():
    """
       Extrae un número del conjunto basado en el número proporcionado.

       Esta función recibe un número a través de una solicitud POST, lo extrae del conjunto y devuelve un mensaje de
        éxito si la operación es exitosa. Si el número no está presente o hay un error durante la extracción,
        devuelve un mensaje de error adecuado.

       Args:
           None

       Returns:
           Response: Un objeto JSON con uno de los siguientes resultados:
               - Si la extracción es exitosa: {'mensaje': 'Número <numero> extraído correctamente.'}
               - Si falta el campo 'numero' en los datos proporcionados:
                   {'error': 'Debes enviar el campo "numero"'}
               - Si ocurre un error durante la extracción:
                   {'error': '<mensaje_error>'}

       Raises:
           ValueError: Si el número proporcionado no es válido.
       """
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({"error": "Token no proporcionado."}), 400

        payload = verify_token(token)
        if 'error' in payload:
            return jsonify(payload), 400

        faltante = conjunto.get_missing_number()
        conjunto.reset()  # Reinicia automáticamente luego de obtener el número
        return jsonify({"numero_faltante": faltante, "mensaje": "Conjunto reiniciado automáticamente."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)


