import psycopg2

from settings import PORT_DB, HOST_DB, DATABASE, USERNAME_DB, PASSWORD_DB


def connect_to_database():
    connection = psycopg2.connect(
        host=HOST_DB,
        port=PORT_DB,
        database=DATABASE,
        user=USERNAME_DB,
        password=PASSWORD_DB
    )
    return connection
