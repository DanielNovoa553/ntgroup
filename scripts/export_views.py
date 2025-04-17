import pandas as pd
from db_conexion.db_data import connectdb

def export_view_to_csv():
    conn = connectdb()
    if conn:
        query = "SELECT * FROM transacciones_diarias;"
        df = pd.read_sql(query, conn)
        df.to_csv("../dataset/transacciones_diarias.csv", index=False)
        print("Vista exportada correctamente.")
        conn.close()

if __name__ == "__main__":
    export_view_to_csv()