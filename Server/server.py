import mysql.connector
from mysql.connector import errorcode

db_config = {
    'user': 'root',
    'password': 'root1234',
    'host': 'localhost',
    'database': 'database'
}

def agregar_usuario(correo, email, password_hash): 
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        insertar_usuario = "INSERT INTO users (correo, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(insertar_usuario, (correo, email, password_hash))
        cnx.commit()
        last_id = cursor.lastrowid
        cursor.close()
        cnx.close()
        return last_id
    except mysql.connector.Error as err:
        print("Error al agregar usuario:", err)
        return None