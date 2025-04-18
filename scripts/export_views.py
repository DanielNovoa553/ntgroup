import pandas as pd
from db_conexion.db_data import connectdb

def export_view_to_csv():
    """
        Exporta los datos de la vista `transacciones_diarias` a un archivo CSV.

        Esta función establece una conexión a la base de datos utilizando la función `connectdb`,
        ejecuta una consulta SQL para obtener todos los registros de la vista `transacciones_diarias`,
        y guarda los resultados en un archivo CSV en el directorio `../dataset_out/` con el nombre
        `transacciones_diarias.csv`.

        Si la exportación es exitosa, se imprime un mensaje de confirmación. En caso de error
        durante el proceso de exportación, se captura la excepción y se imprime un mensaje de error.

        Returns:
            None
        """
    try:
        conn = connectdb()
        if conn:
            query = "SELECT * FROM transacciones_diarias;"
            df = pd.read_sql(query, conn)
            df.to_csv("../dataset_out/transacciones_diarias.csv", index=False)
            print("Vista exportada correctamente.")
            conn.close()
    except Exception as e:
        print(f"Error al exportar la vista: {e}")

