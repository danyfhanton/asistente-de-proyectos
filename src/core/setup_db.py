import pyodbc
from urllib.parse import quote_plus


def ensure_local_sql_database():
    driver = "ODBC Driver 18 for SQL Server"
    server = r"localhost\SQLEXPRESS"
    db_name = "asistente_proyectos"

    master_conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    try:
        conn = pyodbc.connect(master_conn_str, autocommit=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.databases WHERE name = ?", (db_name,))
        row = cur.fetchone()
        if not row:
            print(f"Creando base de datos {db_name} en {server}...")
            cur.execute(f"CREATE DATABASE [{db_name}]")
            print(f"Base de datos {db_name} creada exitosamente.")
        else:
            print(f"Base de datos {db_name} ya existe en {server}.")
        conn.close()
    except Exception as e:
        print(f"Error al verificar/crear base de datos local SQL Server: {e}")


if __name__ == "__main__":
    ensure_local_sql_database()


def test_sqlalchemy_connection():
    from sqlalchemy import create_engine, text
    params = quote_plus(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=asistente_proyectos;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT @@VERSION")).scalar()
        print("SQL Server conectado exitosamente:")
        print(res[:60], "...")


if __name__ == "__main__":
    ensure_local_sql_database()
    test_sqlalchemy_connection()
