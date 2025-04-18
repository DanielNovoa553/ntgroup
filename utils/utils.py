from db_conexion.db_data import connectdb
import hashlib

def validate_email(email):
    try:
        conn = connectdb()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuario WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error al validar el email: {str(e)}")
        return False


# Función para validar la contraseña (debe ser mayor a 8 caracteres)
def validate_password(password):
    try:
        return len(password) >= 8
    except Exception as e:
        print(f"Error al validar la contraseña: {str(e)}")
        return False


def covert_password(password):
    try:
        hash_password = hashlib.md5(password.encode())
        md5_hash = hash_password.hexdigest()
        return md5_hash
    except Exception as e:
        print(f"Error al convertir la contraseña: {str(e)}")
        return False