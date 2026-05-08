import os
import mysql.connector
from dotenv import load_dotenv

db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': '127.0.0.1', # Te recomiendo usar la IP para evitar el error anterior
    'database': os.environ.get('DB'),
    'port': 3306
}

def agregar_usuario(nombre, email, password_hash): 
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # Tabla: Usuario | Columnas: nombre, correo, contrasena
        insertar_usuario = "INSERT INTO Usuario (nombre, correo, contrasena) VALUES (%s, %s, %s)"
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
        # Buscamos en la tabla Usuario por la columna correo
        cursor.execute("SELECT * FROM Usuario WHERE correo = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print("Error al obtener usuario:", err)
        return None

def obtener_perfil_completo(usuario_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        cursor.execute("SELECT nombre, correo, tipo_usuario FROM Usuario WHERE usuario_id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        cursor.execute("SELECT * FROM Direccion WHERE usuario_id = %s", (usuario_id,))
        direcciones = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Metodos_pago WHERE usuario_id = %s", (usuario_id,))
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
    
def agregar_usuario(nombre, email, password_hash): 
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # Nota: Usamos 'contrasena' y 'correo' como en tu SQL
        query = "INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario) VALUES (%s, %s, %s, 'cliente')"
        cursor.execute(query, (nombre, email, password_hash))
        
        # Opcional: Crear el carrito automáticamente para el nuevo usuario
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Carrito (usuario_id) VALUES (%s)", (user_id,))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return user_id
    except mysql.connector.Error as err:
        print("Error al registrar:", err)
        return None