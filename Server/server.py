import os
import mysql.connector
from mysql.connector import errorcode

db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB')
}

def agregar_usuario(nombre, email, password_hash): 
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        insertar_usuario = "INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(insertar_usuario, (nombre, email, password_hash))
        cnx.commit()
        last_id = cursor.lastrowid
        cursor.close()
        cnx.close()
        return last_id
    except mysql.connector.Error as err:
        print("Error al agregar usuario:", err)
        return None
    
def obtener_usuario_por_email(email):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario:", err)
        return None