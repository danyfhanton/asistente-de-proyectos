from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Asistente de Proyectos"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Configuración de SQL Server Local
    SQL_SERVER: str = r"localhost\SQLEXPRESS"
    SQL_DATABASE: str = "asistente_proyectos"
    SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    SQL_TRUSTED_CONNECTION: bool = True
    SQL_TRUST_CERTIFICATE: bool = True
    SQL_USER: str = ""
    SQL_PASSWORD: str = ""

    # Clave de sesión web
    APP_SECRET_KEY: str = "asistente-de-proyectos-secret-local-2026"

    @property
    def DATABASE_URL(self) -> str:
        # Si se especifica usuario y contraseña
        if self.SQL_USER and self.SQL_PASSWORD:
            odbc_str = (
                f"DRIVER={{{self.SQL_DRIVER}}};"
                f"SERVER={self.SQL_SERVER};"
                f"DATABASE={self.SQL_DATABASE};"
                f"UID={self.SQL_USER};"
                f"PWD={self.SQL_PASSWORD};"
                f"TrustServerCertificate={'yes' if self.SQL_TRUST_CERTIFICATE else 'no'};"
            )
        else:
            # Autenticación integrada de Windows (Trusted_Connection)
            odbc_str = (
                f"DRIVER={{{self.SQL_DRIVER}}};"
                f"SERVER={self.SQL_SERVER};"
                f"DATABASE={self.SQL_DATABASE};"
                f"Trusted_Connection={'yes' if self.SQL_TRUSTED_CONNECTION else 'no'};"
                f"TrustServerCertificate={'yes' if self.SQL_TRUST_CERTIFICATE else 'no'};"
            )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
