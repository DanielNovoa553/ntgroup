from dotenv import load_dotenv
import os
import psycopg2
load_dotenv()

def connectdb():
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