from dotenv import load_dotenv
import os
import psycopg2
load_dotenv()

def connectdb():
    """
        Establece una conexión con la base de datos PostgreSQL utilizando las credenciales
        almacenadas en variables de entorno.

        Utiliza la librería `psycopg2` para conectarse a la base de datos, con los parámetros
        de configuración (nombre de base de datos, usuario, contraseña, host y puerto)
        extraídos desde un archivo `.env` mediante la librería `dotenv`.

        Si la conexión es exitosa, devuelve un objeto de conexión; de lo contrario,
        imprime un mensaje de error y retorna `False`.

        Returns:
            psycopg2.extensions.connection | bool:
                Un objeto de conexión a la base de datos si la conexión es exitosa,
                o `False` en caso de error.
        """
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
    except Exception as e:
        print(f'Error al conectar a la base de datos: {e}')
        return False

#probar la conexion
if connectdb():
    print("Conexion exitosa a la base de datos")