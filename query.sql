CREATE DATABASE paleoprints;

USE paleoprints;

-- DROP DATABASE paleoprints;

CREATE TABLE Usuario (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('cliente', 'admin') DEFAULT 'cliente'
);

CREATE TABLE Direccion (
    direccion_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    pais VARCHAR(60) NOT NULL,
    calle VARCHAR(100) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    codigo_postal VARCHAR(10) NOT NULL,
    predeterminada TINYINT(1) DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
);

CREATE TABLE Metodos_pago (
    metodo_de_pago_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    tipo VARCHAR(20) NOT NULL,       -- Ej: 'Visa', 'Mastercard'
    titular VARCHAR(100) NOT NULL,   -- Nombre en la tarjeta
    ultimos4 VARCHAR(4) NOT NULL,    -- Solo los últimos 4 dígitos
    vencimiento VARCHAR(7) NOT NULL, -- Formato MM/YYYY
    predeterminado TINYINT(1) DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
);

CREATE TABLE Carrito (
    carrito_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
);

CREATE TABLE Ropa (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    talla VARCHAR(5),
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),
    imagen_nombre VARCHAR(100)
);

CREATE TABLE Tazas (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    tamano VARCHAR(20),
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),
    imagen_nombre VARCHAR(100)
);

CREATE TABLE Impresiones3D (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    diseno VARCHAR(50),
    tamano VARCHAR(20),
    cantidad_disponible INT DEFAULT 0,
    precio FLOAT NOT NULL,
    imagen_ruta VARCHAR(500),
    imagen_nombre VARCHAR(100)
);

CREATE TABLE Orden (
    orden_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha_creada DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_de_envio DATE,
    estatus VARCHAR(20) DEFAULT 'pendiente',
    productos_id TEXT, -- Usamos TEXT por si la lista es larga
    cantidad_por_producto TEXT,
    pago_total FLOAT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id) ON DELETE CASCADE
);


CREATE INDEX idx_usuario_correo ON Usuario(correo);
CREATE INDEX idx_producto_ropa ON Ropa(nombre);
CREATE INDEX idx_producto_tazas ON Tazas(nombre);
CREATE INDEX idx_impresiones_nombre ON Impresiones3D(nombre);



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
SELECT * FROM Direccion;
SELECT * FROM Usuario;