from db_conexion.db_data import connectdb
import hashlib

def validate_email(email):
    """
        Valida si un email ya está registrado en la base de datos.

        Esta función verifica si el email proporcionado existe en la tabla `usuario` de la base de datos.
         Si el email ya está registrado, retorna `True`, de lo contrario, retorna `False`.

        Args:
            email (str): El correo electrónico que se desea validar.

        Returns:
            bool: `True` si el email ya está registrado, `False` si no lo está.

        Raises:
            Exception: Si ocurre un error durante la conexión o ejecución de la consulta.
        """
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
    """
        Valida que la contraseña tenga al menos 8 caracteres.

        Esta función verifica que la longitud de la contraseña proporcionada sea mayor o igual a 8 caracteres.
         Si cumple con este criterio, retorna `True`, de lo contrario, retorna `False`.

        Args:
            password (str): La contraseña que se desea validar.

        Returns:
            bool: `True` si la contraseña tiene 8 o más caracteres, `False` si no cumple con este requisito.

        Raises:
            Exception: Si ocurre un error inesperado durante la validación.
        """
    try:
        return len(password) >= 8
    except Exception as e:
        print(f"Error al validar la contraseña: {str(e)}")
        return False


def covert_password(password):
    """
        Convierte una contraseña en su hash MD5.

        Esta función toma la contraseña proporcionada, la codifica en formato `utf-8` y luego calcula su hash MD5. El resultado es retornado como un valor hexadecimal.

        Args:
            password (str): La contraseña que se desea convertir.

        Returns:
            str: El hash MD5 de la contraseña en formato hexadecimal.

        Raises:
            Exception: Si ocurre un error durante la conversión de la contraseña.
        """
    try:
        hash_password = hashlib.md5(password.encode())
        md5_hash = hash_password.hexdigest()
        return md5_hash
    except Exception as e:
        print(f"Error al convertir la contraseña: {str(e)}")
        return False


class ConjuntoNumeros:
    """
        Clase para gestionar un conjunto de números del 1 al 100, permitiendo la extracción de un número
        y el cálculo del número faltante basado en la diferencia de sumas.

        Esta clase permite extraer un número del conjunto, calcular el número faltante al realizar la extracción,
        y reiniciar el conjunto de números a su estado original.

        Attributes:
            numeros (list): Lista de números del 1 al 100.
            original_sum (int): Suma de los números del 1 al 100.
            faltante_calculado (bool): Indica si se ha calculado el número faltante.

        Methods:
            extract(numero): Extrae un número del conjunto, validando que el número sea válido y no haya sido extraído previamente.
            get_missing_number(): Calcula y devuelve el número faltante, basado en la diferencia de sumas.
            reset(): Reinicia el conjunto de números a su estado original del 1 al 100.
        """
    def __init__(self):
        """
                Inicializa el conjunto de números con los números del 1 al 100 y reinicia el estado de la clase.
                """
        self.reset()

    def extract(self, numero):
        """
                Extrae un número del conjunto, marcando el número como extraído.

                Args:
                    numero (int): El número que se desea extraer.

                Raises:
                    ValueError: Si el número ya ha sido extraído, no es un entero, o está fuera del rango de 1 a 100.
                """
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
        """
                Calcula el número faltante basado en la diferencia de sumas.

                Returns:
                    int: El número faltante del conjunto.

                Raises:
                    ValueError: Si no se ha extraído ningún número previamente.
                """
        if not self.faltante_calculado:
            raise ValueError("No se ha extraído ningún número.")
        suma_restante = sum(self.numeros)
        return self.original_sum - suma_restante

    def reset(self):
        """
                Reinicia el conjunto de números a su estado original, con números del 1 al 100.

                Resetea la lista de números, la suma original y el estado de extracción de números.
                """
        self.numeros = list(range(1, 101))
        self.original_sum = sum(self.numeros)
        self.faltante_calculado = False
