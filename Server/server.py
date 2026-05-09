import os
import mysql.connector
from dotenv import load_dotenv

db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': '127.0.0.1',
    'database': os.environ.get('DB'),
    'port': 3306
}

def obtener_perfil_completo(usuario_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        # 1. Probar Usuario
        cursor.execute("SELECT nombre, correo, tipo_usuario FROM Usuario WHERE usuario_id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        # 2. Probar Direccion (Aquí es el sospechoso #1)
        try:
            cursor.execute("SELECT * FROM Direccion WHERE usuario_id = %s", (usuario_id,))
            direcciones = cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"DEBUG: El error está en la tabla DIRECCION: {e}")
            direcciones = []

        # 3. Probar Metodos_pago (Aquí es el sospechoso #2)
        try:
            cursor.execute("SELECT * FROM Metodos_pago WHERE usuario_id = %s", (usuario_id,))
            pagos = cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"DEBUG: El error está en la tabla METODOS_PAGO: {e}")
            pagos = []
        
        cursor.close()
        cnx.close()
        return usuario, direcciones, pagos
    except mysql.connector.Error as err:
        print(f"Error general: {err}")
        return None, [], []
    
def obtener_usuario_por_correo(correo):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        # Buscamos por correo, no por ID
        query = "SELECT * FROM Usuario WHERE correo = %s"
        cursor.execute(query, (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario # Devolverá el dict del usuario o None
    except mysql.connector.Error as err:
        print(f"Error al buscar correo: {err}")
        return None


    
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
    

    
# Metodos de pago ---------------------------------------------------------------------------------------------------------------------------------------------------------------    
def agregar_metodo_pago(usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Si esta será la predeterminada, quitamos el check a las anteriores
        if predeterminado:
            cursor.execute("UPDATE Metodos_pago SET predeterminado = 0 WHERE usuario_id = %s", (usuario_id,))

        query = """
            INSERT INTO Metodos_pago (usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado)
        
        cursor.execute(query, valores)
        cnx.commit()
        
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error en DB al agregar pago: {err}")
        return False
    
def eliminar_metodo_pago_db(metodo_id, usuario_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # Aseguramos que el método pertenezca al usuario para que no borren tarjetas ajenas
        query = "DELETE FROM Metodos_pago WHERE metodo_de_pago_id = %s AND usuario_id = %s"
        cursor.execute(query, (metodo_id, usuario_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar pago: {err}")
        return False
    
def establecer_pago_predeterminado(usuario_id, pago_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # Usamos los nombres exactos de tu tabla Metodos_pago
        cursor.execute("UPDATE Metodos_pago SET predeterminado = 0 WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("UPDATE Metodos_pago SET predeterminado = 1 WHERE metodo_de_pago_id = %s AND usuario_id = %s", (pago_id, usuario_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error en DB: {err}")
        return False
    

# Metodos de direccion ---------------------------------------------------------------------------------------------------------------------------------------------------------------
def establecer_direccion_predeterminada(usuario_id, direccion_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        # 1. Quitamos predeterminado a todas las del usuario
        cursor.execute("UPDATE Direccion SET predeterminada = 0 WHERE usuario_id = %s", (usuario_id,))
        # 2. Ponemos predeterminado a la elegida
        cursor.execute("UPDATE Direccion SET predeterminada = 1 WHERE direccion_id = %s AND usuario_id = %s", (direccion_id, usuario_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error en DB: {err}")
        return False
    
def guardar_direccion_db(usuario_id, data, direccion_id=None):
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Usamos .get() para evitar que el programa truene si falta una llave
        calle = data.get('calle')
        ciudad = data.get('ciudad')
        cp = data.get('cp')
        pais = data.get('pais', 'México') # Valor por defecto

        if direccion_id:
            query = "UPDATE Direccion SET calle=%s, ciudad=%s, codigo_postal=%s, pais=%s WHERE direccion_id=%s AND usuario_id=%s"
            cursor.execute(query, (calle, ciudad, cp, pais, direccion_id, usuario_id))
        else:
            query = "INSERT INTO Direccion (calle, ciudad, codigo_postal, pais, usuario_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (calle, ciudad, cp, pais, usuario_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error:
        return False