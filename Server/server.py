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
    
    # server.py

def obtener_perfil_completo(usuario_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        # 1. Datos básicos
        cursor.execute("SELECT nombre, correo, tipo_usuario FROM Usuario WHERE usuario_id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        # 2. Direcciones
        cursor.execute("SELECT * FROM Direccion WHERE usuario_id = %s", (usuario_id,))
        direcciones = cursor.fetchall()
        
        # 3. Métodos de Pago
        cursor.execute("SELECT metodo_de_pago_id, num_tarjeta, fecha_expiracion, direccion_de_facturacion FROM Metodos_pago WHERE usuario_id = %s", (usuario_id,))
        pagos = cursor.fetchall()
        
        cursor.close()
        cnx.close()
        return usuario, direcciones, pagos
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, [], []

def guardar_direccion_db(usuario_id, data, direccion_id=None):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        if direccion_id:
            query = "UPDATE Direccion SET calle=%s, ciudad=%s, codigo_postal=%s, pais=%s WHERE direccion_id=%s AND usuario_id=%s"
            cursor.execute(query, (data['calle'], data['ciudad'], data['cp'], data['pais'], direccion_id, usuario_id))
        else:
            query = "INSERT INTO Direccion (calle, ciudad, codigo_postal, pais, usuario_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (data['calle'], data['ciudad'], data['cp'], data['pais'], usuario_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error:
        return False