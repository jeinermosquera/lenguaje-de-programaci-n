-- ============================================================
-- APOMAT / SELVA SENSORIAL — Esquema de base de datos MySQL
-- Basado exactamente en las tablas que crea inicializar_base_datos() en app.py,
-- más las columnas que el código usa (categoria) y las de contacto.
-- IDEMPOTENTE: seguro de ejecutar más de una vez. NO borra datos.
-- ============================================================

-- CÓMO EJECUTARLO EN PYTHONANYWHERE (consola Bash):
--   mysql -u TU_USUARIO -p TU_NOMBRE_DE_BD < crear_bd.sql
-- (te pedirá la contraseña de la BD de PythonAnywhere)
--
-- Alternativa: pega el contenido completo en la pestaña "Databases"
-- del panel (sección "MySQL" > "Start a console") y ejecútalo ahí.

-- ---------- tabla: usuario ----------
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'cliente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- tabla: producto ----------
CREATE TABLE IF NOT EXISTS producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    imagen VARCHAR(255) NOT NULL,
    precio INT NOT NULL,
    descripcion TEXT,
    caracteristicas TEXT,
    especificaciones TEXT,
    disponible TINYINT DEFAULT 1,
    precio_rebaja INT DEFAULT NULL,
    stock INT DEFAULT 0,
    categoria VARCHAR(50) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- tabla: pedido ----------
CREATE TABLE IF NOT EXISTS pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    referencia VARCHAR(100) UNIQUE NOT NULL,
    total INT NOT NULL,
    estado VARCHAR(30) DEFAULT 'pendiente',
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(30),
    direccion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    costo_envio INT DEFAULT 0,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- tabla: detalle_pedido ----------
CREATE TABLE IF NOT EXISTS detalle_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT,
    nombre_producto VARCHAR(150) NOT NULL,
    precio INT NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedido(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- tabla: contacto ----------
CREATE TABLE IF NOT EXISTS contacto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Columna rol en usuario (idempotente: falla silenciosamente si ya existe)
-- ============================================================
SET @col = (SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuario' AND COLUMN_NAME = 'rol');
SET @sql = IF(@col = 0,
    'ALTER TABLE usuario ADD COLUMN rol VARCHAR(20) DEFAULT ''cliente''',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ============================================================
-- Asegurar que apomat@gmail.com sea administrador.
-- La app también lo hace en cada arranque (inicializar_base_datos).
-- Registra primero esa cuenta en /login si aún no existe.
-- ============================================================
UPDATE usuario SET rol = 'admin' WHERE correo = 'apomat@gmail.com';
