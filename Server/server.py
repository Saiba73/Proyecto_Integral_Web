#server.py
import os
import mysql.connector
from datetime import datetime

# Configuración de la base de datos - Toma los valores del .env
db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': '127.0.0.1',
    'database': os.environ.get('DB'),
    'port': 3306
}

def crear_base_datos_si_no_existe():
    """Crea la base de datos si no existe"""
    try:
        # Conectar sin especificar base de datos
        config_sin_db = {
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASSWORD'),
            'host': '127.0.0.1',
            'port': 3306
        }
        cnx = mysql.connector.connect(**config_sin_db)
        cursor = cnx.cursor()
        
        bd_name = os.environ.get('DB')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {bd_name}")
        print(f"Base de datos '{bd_name}' verificada/creada")
        
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear la base de datos: {err}")
        return False

def crear_orden_db(usuario_id, productos_ids, cantidades, pago_total):
    """Crea una nueva orden en la base de datos"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        from datetime import datetime
        fecha_actual = datetime.now()
        
        query = """INSERT INTO Orden (usuario_id, fecha_creada, productos_id, cantidad_por_producto, pago_total, estatus) 
                   VALUES (%s, %s, %s, %s, %s, 'pendiente')"""
        valores = (usuario_id, fecha_actual, productos_ids, cantidades, pago_total)
        
        cursor.execute(query, valores)
        cnx.commit()
        
        orden_id = cursor.lastrowid
        print(f"Orden creada con ID: {orden_id}")
        
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear orden: {err}")
        return False

# ==================== FUNCIONES DE ADMINISTRADOR ====================
# Agregar estas funciones al final de tu server.py existente
 
def obtener_todos_productos():
    """Obtiene todos los productos de las tres categorías para el panel admin."""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
 
        cursor.execute("SELECT *, 'Ropa' AS categoria FROM Ropa")
        ropa = cursor.fetchall()
 
        cursor.execute("SELECT *, 'Tazas' AS categoria FROM Tazas")
        tazas = cursor.fetchall()
 
        cursor.execute("SELECT *, 'Impresiones3D' AS categoria FROM Impresiones3D")
        impresiones = cursor.fetchall()
 
        cursor.close()
        cnx.close()
        return ropa, tazas, impresiones
    except mysql.connector.Error as err:
        print(f"Error al obtener todos los productos: {err}")
        return [], [], []
 
 
def agregar_producto_db(categoria, nombre, diseno, tam, cantidad, precio, imagen_ruta):
    """Inserta un nuevo producto en la tabla correspondiente."""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
 
        imagen_nombre = imagen_ruta.split('/')[-1] if imagen_ruta else ''
 
        if categoria == 'Ropa':
            q = """INSERT INTO Ropa (nombre, diseno, talla, cantidad_disponible, precio, imagen_ruta, imagen_nombre)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        elif categoria == 'Tazas':
            q = """INSERT INTO Tazas (nombre, diseno, tamano, cantidad_disponible, precio, imagen_ruta, imagen_nombre)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        else:  # Impresiones3D
            q = """INSERT INTO Impresiones3D (nombre, diseno, tamano, cantidad_disponible, precio, imagen_ruta, imagen_nombre)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
 
        cursor.execute(q, (nombre, diseno, tam, cantidad, precio, imagen_ruta, imagen_nombre))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al agregar producto ({categoria}): {err}")
        return False
 
 
def actualizar_producto_db(categoria, producto_id, nombre, diseno, tam, cantidad, precio, imagen_ruta):
    """Actualiza un producto existente en la tabla correspondiente."""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
 
        imagen_nombre = imagen_ruta.split('/')[-1] if imagen_ruta else ''
 
        if categoria == 'Ropa':
            q = """UPDATE Ropa
                   SET nombre=%s, diseno=%s, talla=%s, cantidad_disponible=%s,
                       precio=%s, imagen_ruta=%s, imagen_nombre=%s
                   WHERE producto_id=%s"""
        elif categoria == 'Tazas':
            q = """UPDATE Tazas
                   SET nombre=%s, diseno=%s, tamano=%s, cantidad_disponible=%s,
                       precio=%s, imagen_ruta=%s, imagen_nombre=%s
                   WHERE producto_id=%s"""
        else:  # Impresiones3D
            q = """UPDATE Impresiones3D
                   SET nombre=%s, diseno=%s, tamano=%s, cantidad_disponible=%s,
                       precio=%s, imagen_ruta=%s, imagen_nombre=%s
                   WHERE producto_id=%s"""
 
        cursor.execute(q, (nombre, diseno, tam, cantidad, precio, imagen_ruta, imagen_nombre, producto_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar producto ({categoria}, id={producto_id}): {err}")
        return False
 
 
def eliminar_producto_db(categoria, producto_id):
    """Elimina un producto de la tabla correspondiente."""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
 
        tabla = {'Ropa': 'Ropa', 'Tazas': 'Tazas', 'Impresiones3D': 'Impresiones3D'}.get(categoria)
        if not tabla:
            return False
 
        cursor.execute(f"DELETE FROM {tabla} WHERE producto_id = %s", (producto_id,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar producto ({categoria}, id={producto_id}): {err}")
        return False
 
 
def obtener_todas_ordenes():
    """Obtiene todas las órdenes del sistema para el panel admin."""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Orden ORDER BY fecha_creada DESC")
        ordenes = cursor.fetchall()
        cursor.close()
        cnx.close()
        return ordenes
    except mysql.connector.Error as err:
        print(f"Error al obtener órdenes: {err}")
        return []


# ==================== FUNCIONES DE TABLAS ====================

def crear_tablas():
    """Crea todas las tablas necesarias si no existen en la base de datos"""
    try:
        if not crear_base_datos_si_no_existe():
            return False
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Tabla Usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuario (
                usuario_id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL,
                tipo_usuario ENUM('cliente', 'admin') DEFAULT 'cliente'
            )
        """)
        
        # Tabla Direccion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Direccion (
                direccion_id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                pais VARCHAR(60) NOT NULL,
                calle VARCHAR(100) NOT NULL,
                ciudad VARCHAR(50) NOT NULL,
                codigo_postal VARCHAR(10) NOT NULL,
                predeterminada TINYINT(1) DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
            )
        """)
        
        # Tabla Metodos_pago
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Metodos_pago (
                metodo_de_pago_id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                titular VARCHAR(100) NOT NULL,
                ultimos4 VARCHAR(4) NOT NULL,
                vencimiento VARCHAR(7) NOT NULL,
                predeterminado TINYINT(1) DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
            )
        """)
        
        # Tabla Carrito
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Carrito (
                carrito_id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CarritoItem (
                carrito_item_id INT PRIMARY KEY AUTO_INCREMENT,
                carrito_id INT NOT NULL,
                producto_id INT NOT NULL,
                categoria VARCHAR(20) NOT NULL,
                cantidad INT NOT NULL DEFAULT 1,
                talla_tamano VARCHAR(20),
                precio_unitario FLOAT NOT NULL,
                fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (carrito_id) REFERENCES Carrito(carrito_id) ON DELETE CASCADE
            )
        """)
        
        # Tabla Ropa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ropa (
                producto_id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                diseno VARCHAR(50),
                talla VARCHAR(5),
                cantidad_disponible INT DEFAULT 0,
                precio FLOAT NOT NULL,
                imagen_ruta VARCHAR(500),
                imagen_nombre VARCHAR(100)
            )
        """)
        
        # Tabla Tazas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tazas (
                producto_id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                diseno VARCHAR(50),
                tamano VARCHAR(20),
                cantidad_disponible INT DEFAULT 0,
                precio FLOAT NOT NULL,
                imagen_ruta VARCHAR(500),
                imagen_nombre VARCHAR(100)
            )
        """)
        
        # Tabla Impresiones3D
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Impresiones3D (
                producto_id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                diseno VARCHAR(50),
                tamano VARCHAR(20),
                cantidad_disponible INT DEFAULT 0,
                precio FLOAT NOT NULL,
                imagen_ruta VARCHAR(500),
                imagen_nombre VARCHAR(100)
            )
        """)
        
        # Tabla Orden
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orden (
                orden_id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT NOT NULL,
                fecha_creada DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_de_envio DATE,
                estatus VARCHAR(20) DEFAULT 'pendiente',
                productos_id TEXT,
                cantidad_por_producto TEXT,
                pago_total FLOAT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
            )
        """)
        
        # Índices
        try:
            cursor.execute("CREATE INDEX idx_usuario_correo ON Usuario(correo)")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_producto_ropa ON Ropa(nombre)")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_producto_tazas ON Tazas(nombre)")
        except:
            pass
        try:
            cursor.execute("CREATE INDEX idx_impresiones_nombre ON Impresiones3D(nombre)")
        except:
            pass
        
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Tablas verificadas/creadas correctamente")
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear tablas: {err}")
        return False

def crear_admin_si_no_existe():
    """Crea un usuario administrador por defecto si no existe ninguno"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Verificar si existe algún admin
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE tipo_usuario = 'admin'")
        count_admin = cursor.fetchone()[0]
        
        if count_admin == 0:
            # Crear admin por defecto (contraseña: admin123)
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            cursor.execute("""
                INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario)
                VALUES (%s, %s, %s, 'admin')
            """, ('Administrador', 'admin@paleoprints.com', password_hash))
            
            cnx.commit()        
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al crear admin: {err}")
        return False

def insertar_productos_iniciales():
    """Inserta productos solo si las tablas estan vacias"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Verificar Ropa
        cursor.execute("SELECT COUNT(*) FROM Ropa")
        count_ropa = cursor.fetchone()[0]
        
        if count_ropa == 0:
            productos_ropa = [
                ('Pachycephalosaurus Hoodie - Blanco', 'Hoodie', 'S', 15, 39.99, 'imagenes/productos/Pachy-blanco-Hoodie.jpg', 'Pachy-blanco-Hoodie.jpg'),
                ('Pachycephalosaurus T-shirt - Blanco', 'T-shirt', 'M', 10, 22.99, 'imagenes/productos/Pachy-blanco-Tshirt.jpg', 'Pachy-blanco-Tshirt.jpg'),
                ('Pachycephalosaurus Sweatshirt - Negro', 'Sweatshirt', 'L', 20, 32.99, 'imagenes/productos/Pachy-negro-Sweatshirt.jpg', 'Pachy-negro-Sweatshirt.jpg'),
                ('Therizinosaurus Sweatshirt - Blanco', 'Sweatshirt', 'S', 10, 32.99, 'imagenes/productos/Theriz-blanco-Sweatshirt.jpg', 'Theriz-blanco-Sweatshirt.jpg'),
                ('Therizinosaurus T-shirt - Blanco', 'T-shirt', 'M', 12, 22.99, 'imagenes/productos/Theriz-blanco-Tshirt.jpg', 'Theriz-blanco-Tshirt.jpg'),
                ('Tyrannosaurus Hoodie - Blanco', 'Hoodie', 'L', 21, 39.99, 'imagenes/productos/Trex-blanco-Hoodie.jpg', 'Trex-blanco-Hoodie.jpg'),
                ('Tyrannosaurus Sweatshirt - Negro', 'Sweatshirt', 'M', 6, 32.99, 'imagenes/productos/Trex-negro-Sweatshirt.jpg', 'Trex-negro-Sweatshirt.jpg'),
                ('Tyrannosaurus T-shirt - Negro', 'T-shirt', 'XL', 8, 22.99, 'imagenes/productos/Trex-negro-Tshirt.jpg', 'Trex-negro-Tshirt.jpg')
            ]
            
            query = """INSERT INTO Ropa (nombre, diseno, talla, cantidad_disponible, precio, imagen_ruta, imagen_nombre) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.executemany(query, productos_ropa)
            print(f"Insertados {len(productos_ropa)} productos de ropa")
        
        # Verificar Tazas
        cursor.execute("SELECT COUNT(*) FROM Tazas")
        count_tazas = cursor.fetchone()[0]
        
        if count_tazas == 0:
            productos_tazas = [
                ('Pachycephalosaurus - Blanca', 'Taza', '11 OZ', 16, 19.99, 'imagenes/productos/Pachy-blanca-taza.jpg', 'Pachy-blanca-taza.jpg'),
                ('Therizinosaurus - Blanca', 'Taza', '11 OZ', 8, 19.99, 'imagenes/productos/Theriz-blanca-taza.jpg', 'Theriz-blanca-taza.jpg'),
                ('Tyrannosaurus - Blanca', 'Taza', '11 OZ', 21, 19.99, 'imagenes/productos/Trex-blanca-taza.jpg', 'Trex-blanca-taza.jpg'),
                ('Tyrannosaurus - Negra', 'Taza', '11 OZ', 14, 19.99, 'imagenes/productos/Trex-negra-taza.jpg', 'Trex-negra-taza.jpg')
            ]
            
            query = """INSERT INTO Tazas (nombre, diseno, tamano, cantidad_disponible, precio, imagen_ruta, imagen_nombre) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.executemany(query, productos_tazas)
            print(f"Insertados {len(productos_tazas)} productos de tazas")
        
        # Verificar Impresiones3D
        cursor.execute("SELECT COUNT(*) FROM Impresiones3D")
        count_impresiones = cursor.fetchone()[0]
        
        if count_impresiones == 0:
            productos_impresiones = [
                ('Triceratops', 'Cartoon', '15cm', 25, 11.99, 'imagenes/productos/Triceratops-3d.jpg', 'Triceratops-3d.jpg'),
                ('Pterodactyl', 'Figura', '10cm', 21, 9.99, 'imagenes/productos/Pterodactyl-3d.jpg', 'Pterodactyl-3d.jpg'),
                ('Brachiosaurus', 'Llavero', '5cm', 15, 4.99, 'imagenes/productos/Brachiosaurus-3d.jpg', 'Brachiosaurus-3d.jpg')
            ]
            
            query = """INSERT INTO Impresiones3D (nombre, diseno, tamano, cantidad_disponible, precio, imagen_ruta, imagen_nombre) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.executemany(query, productos_impresiones)
            print(f"Insertados {len(productos_impresiones)} productos de impresiones 3D")
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al insertar productos: {err}")
        return False

# ==================== FUNCIONES DE USUARIO ====================

def obtener_perfil_completo(usuario_id):
    """Obtiene toda la información de perfil de un usuario"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        cursor.execute("SELECT nombre, correo, tipo_usuario FROM Usuario WHERE usuario_id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        try:
            cursor.execute("SELECT * FROM Direccion WHERE usuario_id = %s", (usuario_id,))
            direcciones = cursor.fetchall()
        except mysql.connector.Error:
            direcciones = []

        try:
            cursor.execute("SELECT * FROM Metodos_pago WHERE usuario_id = %s", (usuario_id,))
            pagos = cursor.fetchall()
        except mysql.connector.Error:
            pagos = []
        
        cursor.close()
        cnx.close()
        return usuario, direcciones, pagos
    except mysql.connector.Error as err:
        print(f"Error general: {err}")
        return None, [], []
    
def obtener_usuario_por_correo(correo):
    """Busca un usuario por su correo electrónico"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT * FROM Usuario WHERE correo = %s"
        cursor.execute(query, (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        cnx.close()
        return usuario
    except mysql.connector.Error as err:
        print(f"Error al buscar correo: {err}")
        return None

def agregar_usuario(nombre, email, password_hash): 
    """Registra un nuevo usuario en el sistema"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = "INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario) VALUES (%s, %s, %s, 'cliente')"
        cursor.execute(query, (nombre, email, password_hash))
        
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Carrito (usuario_id) VALUES (%s)", (user_id,))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return user_id
    except mysql.connector.Error as err:
        print("Error al registrar:", err)
        return None

# ==================== FUNCIONES DE PRODUCTOS ====================

def obtener_productos_ropa():
    """Obtiene todos los productos de ropa disponibles"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Ropa WHERE cantidad_disponible > 0")
        productos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return productos
    except mysql.connector.Error as err:
        print(f"Error al obtener productos de ropa: {err}")
        return []

def obtener_productos_tazas():
    """Obtiene todos los productos de tazas disponibles"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tazas WHERE cantidad_disponible > 0")
        productos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return productos
    except mysql.connector.Error as err:
        print(f"Error al obtener productos de tazas: {err}")
        return []

def obtener_productos_impresiones():
    """Obtiene todos los productos de impresiones 3D disponibles"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Impresiones3D WHERE cantidad_disponible > 0")
        productos = cursor.fetchall()
        cursor.close()
        cnx.close()
        return productos
    except mysql.connector.Error as err:
        print(f"Error al obtener productos de impresiones 3D: {err}")
        return []

def obtener_producto_por_id_con_prefijo(producto_id_con_prefijo):
    """
    Recibe un ID con prefijo como 'ropa-1', 'tazas-3', 'impresiones-2'
    y devuelve el producto de la tabla correspondiente
    """
    try:
        # Separar el prefijo del ID numérico
        partes = producto_id_con_prefijo.split('-')
        if len(partes) != 2:
            return None
        
        categoria = partes[0]  # 'ropa', 'tazas' o 'impresiones'
        producto_id = int(partes[1])
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        # Determinar la tabla y el campo de medida según la categoría
        if categoria == 'ropa':
            tabla = 'Ropa'
            campo_medida = 'talla'
        elif categoria == 'tazas':
            tabla = 'Tazas'
            campo_medida = 'tamano'
        elif categoria == 'impresiones':
            tabla = 'Impresiones3D'
            campo_medida = 'tamano'
        else:
            cursor.close()
            cnx.close()
            return None
        
        # Consultar el producto
        query = f"SELECT *, '{categoria}' as categoria, {campo_medida} as medida FROM {tabla} WHERE producto_id = %s"
        cursor.execute(query, (producto_id,))
        producto = cursor.fetchone()
        
        cursor.close()
        cnx.close()
        return producto
        
    except mysql.connector.Error as err:
        print(f"Error al buscar producto: {err}")
        return None
    except ValueError:
        print(f"Error: ID inválido {producto_id_con_prefijo}")
        return None

def obtener_productos_relacionados(categoria, producto_id, limite=4):
    """Obtiene productos relacionados de la misma categoría"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        if categoria == 'ropa':
            tabla = 'Ropa'
        elif categoria == 'tazas':
            tabla = 'Tazas'
        else:
            tabla = 'Impresiones3D'
        
        query = f"SELECT * FROM {tabla} WHERE producto_id != %s AND cantidad_disponible > 0 LIMIT %s"
        cursor.execute(query, (producto_id, limite))
        relacionados = cursor.fetchall()
        
        cursor.close()
        cnx.close()
        return relacionados
    except mysql.connector.Error as err:
        print(f"Error al obtener productos relacionados: {err}")
        return []

# ==================== FUNCIONES DE CARRITO ====================

def obtener_carrito_activo(usuario_id):
    """Obtiene el carrito activo del usuario o crea uno nuevo"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        # Buscar carrito existente
        cursor.execute("SELECT carrito_id FROM Carrito WHERE usuario_id = %s ORDER BY fecha_creacion DESC LIMIT 1", (usuario_id,))
        carrito = cursor.fetchone()
        
        if not carrito:
            # Crear nuevo carrito
            cursor.execute("INSERT INTO Carrito (usuario_id) VALUES (%s)", (usuario_id,))
            cnx.commit()
            carrito_id = cursor.lastrowid
        else:
            carrito_id = carrito['carrito_id']
        
        cursor.close()
        cnx.close()
        return carrito_id
    except mysql.connector.Error as err:
        print(f"Error al obtener carrito: {err}")
        return None

def agregar_al_carrito_db(usuario_id, producto_id, categoria, cantidad, talla_tamano, precio_unitario):
    """Agrega un producto al carrito del usuario"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return False
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # Verificar si el producto ya está en el carrito (misma categoría, producto y talla)
        cursor.execute("""
            SELECT carrito_item_id, cantidad FROM CarritoItem 
            WHERE carrito_id = %s AND producto_id = %s AND categoria = %s AND talla_tamano = %s
        """, (carrito_id, producto_id, categoria, talla_tamano))
        
        item = cursor.fetchone()
        
        if item:
            # Actualizar cantidad
            nueva_cantidad = item[1] + cantidad
            cursor.execute("""
                UPDATE CarritoItem SET cantidad = %s WHERE carrito_item_id = %s
            """, (nueva_cantidad, item[0]))
        else:
            # Insertar nuevo item
            cursor.execute("""
                INSERT INTO CarritoItem (carrito_id, producto_id, categoria, cantidad, talla_tamano, precio_unitario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (carrito_id, producto_id, categoria, cantidad, talla_tamano, precio_unitario))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al agregar al carrito: {err}")
        return False

def obtener_carrito_con_productos(usuario_id):
    """Obtiene todos los productos del carrito del usuario"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return []
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT ci.*, 
                   CASE 
                       WHEN ci.categoria = 'ropa' THEN r.nombre
                       WHEN ci.categoria = 'tazas' THEN t.nombre
                       WHEN ci.categoria = 'impresiones' THEN i.nombre
                   END as nombre_producto
            FROM CarritoItem ci
            LEFT JOIN Ropa r ON ci.categoria = 'ropa' AND ci.producto_id = r.producto_id
            LEFT JOIN Tazas t ON ci.categoria = 'tazas' AND ci.producto_id = t.producto_id
            LEFT JOIN Impresiones3D i ON ci.categoria = 'impresiones' AND ci.producto_id = i.producto_id
            WHERE ci.carrito_id = %s
        """, (carrito_id,))
        
        items = cursor.fetchall()
        cursor.close()
        cnx.close()
        return items
    except mysql.connector.Error as err:
        print(f"Error al obtener carrito: {err}")
        return []

def eliminar_item_carrito(usuario_id, carrito_item_id):
    """Elimina un item específico del carrito"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return False
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        cursor.execute("""
            DELETE FROM CarritoItem 
            WHERE carrito_item_id = %s AND carrito_id = %s
        """, (carrito_item_id, carrito_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar item: {err}")
        return False

def obtener_carrito_con_detalles(usuario_id):
    """Obtiene todos los items del carrito del usuario con detalles del producto"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return [], 0
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT ci.*, 
                   CASE 
                       WHEN ci.categoria = 'ropa' THEN r.nombre
                       WHEN ci.categoria = 'tazas' THEN t.nombre
                       WHEN ci.categoria = 'impresiones' THEN i.nombre
                   END as nombre_producto,
                   CASE 
                       WHEN ci.categoria = 'ropa' THEN r.imagen_ruta
                       WHEN ci.categoria = 'tazas' THEN t.imagen_ruta
                       WHEN ci.categoria = 'impresiones' THEN i.imagen_ruta
                   END as imagen_ruta
            FROM CarritoItem ci
            LEFT JOIN Ropa r ON ci.categoria = 'ropa' AND ci.producto_id = r.producto_id
            LEFT JOIN Tazas t ON ci.categoria = 'tazas' AND ci.producto_id = t.producto_id
            LEFT JOIN Impresiones3D i ON ci.categoria = 'impresiones' AND ci.producto_id = i.producto_id
            WHERE ci.carrito_id = %s
        """, (carrito_id,))
        
        items = cursor.fetchall()
        
        # Calcular total
        total = sum(item['precio_unitario'] * item['cantidad'] for item in items)
        
        cursor.close()
        cnx.close()
        return items, total
    except mysql.connector.Error as err:
        print(f"Error al obtener carrito: {err}")
        return [], 0


def actualizar_cantidad_item_db(usuario_id, carrito_item_id, delta):
    """Actualiza la cantidad de un item en el carrito sumando delta"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return False
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        
        # Obtener cantidad actual
        cursor.execute("SELECT cantidad FROM CarritoItem WHERE carrito_item_id = %s AND carrito_id = %s", 
                      (carrito_item_id, carrito_id))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            cnx.close()
            return False
        
        nueva_cantidad = item['cantidad'] + delta
        
        if nueva_cantidad <= 0:
            # Eliminar si la cantidad es 0 o menor
            cursor.execute("DELETE FROM CarritoItem WHERE carrito_item_id = %s AND carrito_id = %s",
                          (carrito_item_id, carrito_id))
        else:
            # Actualizar cantidad
            cursor.execute("UPDATE CarritoItem SET cantidad = %s WHERE carrito_item_id = %s AND carrito_id = %s",
                          (nueva_cantidad, carrito_item_id, carrito_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar cantidad: {err}")
        return False


def eliminar_item_carrito_db(usuario_id, carrito_item_id):
    """Elimina un item específico del carrito"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return False
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        cursor.execute("""
            DELETE FROM CarritoItem 
            WHERE carrito_item_id = %s AND carrito_id = %s
        """, (carrito_item_id, carrito_id))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar item: {err}")
        return False

def vaciar_carrito(usuario_id):
    """Vacía todo el carrito del usuario"""
    try:
        carrito_id = obtener_carrito_activo(usuario_id)
        if not carrito_id:
            return False
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        cursor.execute("DELETE FROM CarritoItem WHERE carrito_id = %s", (carrito_id,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error al vaciar carrito: {err}")
        return False

# ==================== FUNCIONES DE DIRECCIONES ====================

def establecer_direccion_predeterminada(usuario_id, direccion_id):
    """Marca una dirección como la predeterminada para un usuario"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("UPDATE Direccion SET predeterminada = 0 WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("UPDATE Direccion SET predeterminada = 1 WHERE direccion_id = %s AND usuario_id = %s", (direccion_id, usuario_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error en DB: {err}")
        return False
    
def guardar_direccion_db(usuario_id, data, direccion_id=None):
    """Guarda o actualiza una dirección para un usuario"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        calle = data.get('calle')
        ciudad = data.get('ciudad')
        cp = data.get('cp')
        pais = data.get('pais', 'México')

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
    except mysql.connector.Error as err:
        print(f"Error al guardar dirección: {err}")
        return False

# ==================== FUNCIONES DE METODOS DE PAGO ====================

def agregar_metodo_pago(usuario_id, tipo, titular, ultimos4, vencimiento, predeterminado):
    """Registra un nuevo método de pago para un usuario"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

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
    """Elimina un método de pago de un usuario"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
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
    """Marca un método de pago como predeterminado"""
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("UPDATE Metodos_pago SET predeterminado = 0 WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("UPDATE Metodos_pago SET predeterminado = 1 WHERE metodo_de_pago_id = %s AND usuario_id = %s", (pago_id, usuario_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error en DB: {err}")
        return False