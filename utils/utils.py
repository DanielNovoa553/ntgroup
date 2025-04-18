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


class ConjuntoNumeros:
    def __init__(self):
        self.reset()

    def extract(self, numero):
        if self.faltante_calculado:
            raise ValueError("Ya se extrajo un número. Solo se permite una extracción.")
        if not isinstance(numero, int):
            raise ValueError("El número debe ser un entero.")
        if numero < 1 or numero > 100:
            raise ValueError("El número debe estar entre 1 y 100.")
        if numero not in self.numeros:
            raise ValueError("El número ya fue extraído o no existe.")
        self.numeros.remove(numero)
        self.faltante_calculado = True

    def get_missing_number(self):
        if not self.faltante_calculado:
            raise ValueError("No se ha extraído ningún número.")
        suma_restante = sum(self.numeros)
        return self.original_sum - suma_restante

    def reset(self):
        self.numeros = list(range(1, 101))
        self.original_sum = sum(self.numeros)
        self.faltante_calculado = False
