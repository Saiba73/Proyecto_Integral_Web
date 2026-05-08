CREATE DATABASE paleoprints;

USE paleoprints;

CREATE TABLE Usuario (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    correo VARCHAR(30) UNIQUE NOT NULL,
    contrasena VARCHAR(20) NOT NULL,
    tipo_usuario ENUM('cliente', 'admin') DEFAULT 'cliente'
);


CREATE TABLE Direccion (
    direccion_id INT PRIMARY KEY AUTO_INCREMENT,
    pais VARCHAR(60) NOT NULL,
    calle VARCHAR(30) NOT NULL,
    ciudad VARCHAR(15) NOT NULL,
    codigo_postal INT(10) NOT NULL
);


CREATE TABLE Metodos_pago (
    metodo_de_pago_id INT PRIMARY KEY AUTO_INCREMENT,
    num_tarjeta VARCHAR(19) NOT NULL,
    fecha_expiracion VARCHAR(4) NOT NULL,
    cvv INT(3) NOT NULL,
    direccion_de_facturacion VARCHAR(500) NOT NULL
);


CREATE TABLE Carrito (
    carrito_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
);


CREATE TABLE Cliente (
    cliente_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT UNIQUE NOT NULL,
    direccion_id INT,
    metodo_de_pago_id INT,
    carrito_id INT,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE,
    FOREIGN KEY (direccion_id) REFERENCES Direccion(direccion_id) ON DELETE SET NULL,
    FOREIGN KEY (metodo_de_pago_id) REFERENCES Metodos_pago(metodo_de_pago_id) ON DELETE SET NULL,
    FOREIGN KEY (carrito_id) REFERENCES Carrito(carrito_id) ON DELETE SET NULL
);


CREATE TABLE Ropa (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    talla VARCHAR(5),
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),  -- Ruta de la imagen en el servidor
    imagen_nombre VARCHAR(100)  -- Nombre original del archivo
);


CREATE TABLE Tazas (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    tamano VARCHAR(20),  -- Cambiado de talla a tamaño
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),
    imagen_nombre VARCHAR(100)
);


CREATE TABLE Impresiones3D (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    tamaño VARCHAR(20),
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),
    imagen_nombre VARCHAR(100)
);


CREATE TABLE Orden (
    orden_id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    fecha_creada DATE NOT NULL,
    fecha_de_envio DATE,
    estatus VARCHAR(20) DEFAULT 'pendiente',
    productos_id VARCHAR(500),  -- IDs separados por coma (ej: "1,2,3")
    cantidad_por_producto VARCHAR(500),
    pago_total FLOAT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES Cliente(cliente_id) ON DELETE CASCADE
);


CREATE TABLE Ventas (
    venta_id INT PRIMARY KEY AUTO_INCREMENT,
    orden_id INT NOT NULL,
    cliente_id INT NOT NULL,
    fecha_creada DATE NOT NULL,
    productos_id VARCHAR(500),
    cantidad_por_producto VARCHAR(500),
    estatus VARCHAR(20),
    pago_total FLOAT,
    FOREIGN KEY (orden_id) REFERENCES Orden(orden_id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_id) REFERENCES Cliente(cliente_id) ON DELETE CASCADE
);


CREATE INDEX idx_usuario_correo ON Usuario(correo);
CREATE INDEX idx_producto_nombre ON Ropa(nombre);
CREATE INDEX idx_tazas_nombre ON Tazas(nombre);
CREATE INDEX idx_impresiones_nombre ON Impresiones3D(nombre);

INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario) 
VALUES ('Administrador', 'admin@ejemplo.com', '1234', 'admin');

INSERT INTO Ropa (nombre, diseno, talla, cantidad_disponible, precio, imagen_ruta, imagen_nombre) VALUES
('Pachycephalosaurus Hoodie - Blanco', 'Hoodie','S', '15', '39.99', 'static/imagenes/productos/Pachy-blanco-Hoodie.jpg', 'Pachy-blanco-Hoodie.jpg'),
('Pachycephalosaurus T-shirt - Blanco', 'T-shirt','M', '10', '22.99', 'static/imagenes/productos/Pachy-blanco-Tshirt.jpg', 'Pachy-blanco-Tshirt.jpg'),
('Pachycephalosaurus Sweatshirt - Negro', 'Sweatshirt','L', '20', '32.99', 'static/imagenes/productos/Pachy-negro-Sweatshirt.jpg', 'Pachy-negro-Sweatshirt.jpg'),
('Therizinosaurus Sweatshirt - Blanco', 'Sweatshirt','S', '10', '32.99', 'static/imagenes/productos/Theriz-blanco-Sweatshirt.jpg', 'Theriz-blanco-Sweatshirt.jpg'),
('Therizinosaurus T-shirt - Blanco', 'T-shirt','M', '12', '22.99', 'static/imagenes/productos/Theriz-blanco-Tshirt.jpg', 'Theriz-blanco-Tshirt.jpg'),
('Tyrannosaurus Hoodie - Blanco', 'Hoodie','L', '21', '39.99', 'static/imagenes/productos/Trex-blanco-Hoodie.jpg', 'Trex-blanco-Hoodie.jpg'),
('Tyrannosaurus Sweatshirt - Negro', 'Sweatshirt','M', '6', '32.99', 'static/imagenes/productos/Trex-negro-Sweatshirt.jpg', 'Trex-negro-Sweatshirt.jpg'),
('Tyrannosaurus T-shirt - Negro', 'T-shirt','XL', '8', '22.99', 'static/imagenes/productos/Trex-negro-Tshirt.jpg', 'Trex-negro-Tshirt.jpg');

INSERT INTO Tazas (nombre, diseno, tamano, cantidad_disponible, precio, imagen_ruta, imagen_nombre) VALUES
('Pachycephalosaurus - Blanca', 'Taza','11 OZ', '16', '19.99', 'static/imagenes/productos/Pachy-blanca-taza.jpg', 'Pachy-blanca-taza.jpg'),
('Therizinosaurus - Blanca', 'Taza','11 OZ', '8', '19.99', 'static/imagenes/productos/Theriz-blanca-taza.jpg', 'Theriz-blanca-taza.jpg'),
('Tyrannosaurus - Blanca', 'Taza','11 OZ', '21', '19.99', 'static/imagenes/productos/Trex-blanca-taza.jpg', 'Trex-blanca-taza.jpg'),
('Tyrannosaurus - Negra', 'Taza','11 OZ', '14', '19.99', 'static/imagenes/productos/Trex-negra-tazat.jpg', 'Trex-negra-taza.jpg');

SELECT * FROM Ropa;
SELECT * FROM Tazas;