import os
import pandas as pd
from db_conexion.db_data import connectdb
from datetime import datetime


def load_data(conn):
    cur = conn.cursor()

    # Cargar y guardar companies
    input_path = os.path.join("..", "dataset", "companies.csv")
    companies = pd.read_csv(input_path)
    for _, row in companies.iterrows():
        cur.execute("""
            INSERT INTO companies (id, company_name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (row['id'], row['name']))

    # Cargar y guardar charges
    input_path = os.path.join("..", "dataset", "charges.csv")
    charges = pd.read_csv(input_path)

    # Manejar valores NaN en las columnas de fecha
    for _, row in charges.iterrows():
        # Reemplazar NaN en created_at con la fecha actual
        created_at = None if pd.isna(row['created_at']) else row['created_at']

        # Usar paid_at en lugar de updated_at
        paid_at = None if pd.isna(row['paid_at']) else row['paid_at']

        # Si created_at es None, asignamos la fecha actual
        if created_at is None:
            created_at = datetime.now()

        # Si paid_at es None, asignamos la fecha actual


        cur.execute("""
            INSERT INTO charges (id, company_id, amount, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            row['id'],
            row['company_id'],
            row['amount'],
            row['status'],
            created_at,
            paid_at
        ))

    conn.commit()
    cur.close()
    print("Datos cargados exitosamente en la base de datos.")


if __name__ == "__main__":
    conn = connectdb()
    if conn:
        load_data(conn)
        conn.close()
