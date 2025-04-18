import os
import pandas as pd
from db_conexion.db_data import connectdb
from scripts.transform import transform_data
from scripts.export_views import export_view_to_csv

def load_data():
    try:
        print("Iniciando transformación de datos...")
        transform_data()

        con = connectdb()
        cur = con.cursor()

        print("Cargando datos transformados a la base de datos...")

        # Cargar y guardar companies
        input_path = os.path.join("..", "dataset_out", "companies.csv")
        companies = pd.read_csv(input_path)
        for _, row in companies.iterrows():
            cur.execute("""
                INSERT INTO companies (id, company_name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (row['id'], row['name']))

        # Cargar y guardar charges
        input_path = os.path.join("..", "dataset_out", "charges.csv")
        charges = pd.read_csv(input_path)

        for _, row in charges.iterrows():
            paid_at = None if pd.isna(row['paid_at']) else row['paid_at']

            cur.execute("""
                INSERT INTO charges (id, company_id, amount, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                row['id'],
                row['company_id'],
                row['amount'],
                row['status'],
                row['created_at'],
                paid_at
            ))

        con.commit()
        cur.close()
        con.close()

        print("Datos cargados exitosamente en la base de datos.")

        print("Exportando vista transacciones_diarias...")
        export_view_to_csv()

    except Exception as e:
        print(f"Error al ejecutar el flujo ETL completo: {e}")


if __name__ == "__main__":
    load_data()
