import mysql.connector
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()


def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "4000")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=os.getenv("DB_SSL_CA") or None,
        ssl_verify_cert=True if os.getenv("DB_SSL_CA") else False,
        ssl_verify_identity=True if os.getenv("DB_SSL_CA") else False
    )

    return connection

