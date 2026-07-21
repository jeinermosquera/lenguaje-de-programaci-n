# app.py - aplicación principal de Flask para el proyecto de login
from pathlib import Path
import os
import json
import random
import time
from dotenv import load_dotenv
from flask import Flask, redirect, request, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename

load_dotenv()

# para conectar con la base de datos MySQL
import mysql.connector
from mysql.connector import Error

# encripta las contraseñas y verifica las contraseñas en el login
from werkzeug.security import generate_password_hash, check_password_hash

# correo del administrador (dueño)
ADMIN_EMAIL = "apomat@gmail.com"

# Stripe — modo test por defecto
import stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")
stripe.api_key = STRIPE_SECRET_KEY

# la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent

LOGIN_DIR = BASE_DIR / "login"
SITE_DIR = BASE_DIR / "web"
STATIC_DIR = BASE_DIR / "static"

# crear la app de Flask
app = Flask(__name__)
app.secret_key = "clave_super_secreta"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

def inicializar_base_datos():
    """Crea las tablas usuario, producto, pedido, detalle_pedido y contacto si no existen.
    Agrega columnas precio_rebaja, stock y costo_envio si faltan."""
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS producto (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                imagen VARCHAR(255) NOT NULL,
                precio INT NOT NULL,
                descripcion TEXT,
                caracteristicas TEXT,
                especificaciones TEXT,
                disponible TINYINT DEFAULT 1,
                precio_rebaja INT DEFAULT NULL
            )
        """)

        try:
            cursor.execute("ALTER TABLE producto ADD COLUMN precio_rebaja INT DEFAULT NULL")
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE producto ADD COLUMN stock INT DEFAULT 0")
        except Error:
            pass

        try:
            cursor.execute("UPDATE producto SET stock = 10 WHERE stock IS NULL OR stock = 0")
        except Error:
            pass

        cursor.execute("""
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
                FOREIGN KEY (usuario_id) REFERENCES usuario(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_pedido (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pedido_id INT NOT NULL,
                producto_id INT,
                nombre_producto VARCHAR(150) NOT NULL,
                precio INT NOT NULL,
                cantidad INT NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedido(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES producto(id)
            )
        """)

        try:
            cursor.execute("ALTER TABLE pedido ADD COLUMN costo_envio INT DEFAULT 0")
        except:
            pass



    except Error as error:
        print(f"Error al inicializar BD: {error}")
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

@app.after_request
def add_header(response):
    """Desactiva caché del navegador en todas las respuestas."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def get_connection():
    """Retorna conexión MySQL a jeiner_db (127.0.0.1, root sin contraseña)."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="jeiner_db"
    )

def producto_db_a_dict(row):
    """Convierte una fila de la BD (tupla) en dict con precios formateados y JSONs parseados."""
    precio_rebaja = row[8] if len(row) > 8 else None
    stock = row[9] if len(row) > 9 else 0
    return {
        "id": row[0],
        "nombre": row[1],
        "imagen": row[2],
        "precio": row[3],
        "descripcion": row[4] or "",
        "caracteristicas": json.loads(row[5]) if row[5] else [],
        "especificaciones": json.loads(row[6]) if row[6] else [],
        "disponible": bool(row[7]),
        "precio_rebaja": precio_rebaja,
        "precio_formateado": f"$ {row[3]:,.0f}".replace(",", "."),
        "precio_rebaja_formateado": f"$ {precio_rebaja:,.0f}".replace(",", ".") if precio_rebaja else None,
        "en_rebaja": precio_rebaja is not None and precio_rebaja > 0,
        "stock": stock if stock is not None else 0
    }

@app.route("/")
def home():
    """Sirve login/index.html (página pública de login/registro)."""
    return send_from_directory(LOGIN_DIR, "index.html")

@app.route("/css/<path:filename>")
def css_files(filename):
    """Sirve archivos CSS del login."""
    return send_from_directory(LOGIN_DIR / "css", filename)

@app.route("/img/<path:filename>")
def img_files(filename):
    """Sirve imágenes del login."""
    return send_from_directory(LOGIN_DIR / "img", filename)

@app.route("/favicon/<path:filename>")
def favicon_files(filename):
    """Sirve favicons del login."""
    return send_from_directory(LOGIN_DIR / "favicon", filename)

@app.route("/site/css/<path:filename>")
def site_css(filename):
    """Sirve archivos CSS del sitio protegido."""
    return send_from_directory(SITE_DIR / "css", filename)

@app.route("/site/img/<path:filename>")
def site_img(filename):
    """Sirve imágenes del sitio protegido."""
    return send_from_directory(SITE_DIR / "img", filename)

@app.route("/site/js/<path:filename>")
def site_js(filename):
    """Sirve archivos JS del sitio protegido."""
    return send_from_directory(SITE_DIR / "js", filename)

@app.route("/site/favicon/<path:filename>")
def site_favicon(filename):
    """Sirve favicons del sitio protegido."""
    return send_from_directory(SITE_DIR / "favicon", filename)

@app.route("/static/img/<path:filename>")
def static_img(filename):
    """Sirve imágenes estáticas desde static/img/ (ruta opcional)."""
    return send_from_directory(STATIC_DIR / "img", filename)

@app.route("/register", methods=["POST"])
def register():
    """Registra un nuevo usuario, hashea la contraseña, inicia sesión y redirige."""

    full_name = request.form.get("nombre", "").strip()
    email = request.form.get("correo", "").strip().lower()
    password = request.form.get("contrasena", "")

    if len(full_name) < 3:
        return redirect("/?error=nombre_invalido")

    if "@" not in email:
        return redirect("/?error=email_invalido")

    if len(password) < 8:
        return redirect("/?error=password_corta")

    password_hash = generate_password_hash(password)

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO usuario (nombre, correo, contrasena)
        VALUES (%s, %s, %s)
        """

        values = (full_name, email, password_hash)

        cursor.execute(query, values)
        connection.commit()
        nuevo_id = cursor.lastrowid

    except Error as error:
        print(error)

        if getattr(error, "errno", None) == 1062:
            return redirect("/?error=correo_existente")

        return f"Error MySQL: {error}", 500

    finally:
        if "cursor" in locals():
            cursor.close()

        if "connection" in locals() and connection.is_connected():
            connection.close()

    # iniciar sesión automáticamente después del registro
    session["logueado"] = True
    session["usuario_id"] = nuevo_id
    session["nombre"] = full_name
    session["admin"] = (email == ADMIN_EMAIL)

    if session["admin"]:
        return redirect("/admin?register=success")

    return redirect("/dashboard?register=success")

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 30

@app.route("/login", methods=["POST"])
def login():
    """Autentica usuario contra BD, inicia sesión y redirige a dashboard o admin."""

    now = time.time()
    intentos = session.get("login_attempts", 0)
    bloqueado_hasta = session.get("login_locked_until", 0)

    if bloqueado_hasta > now:
        segundos_restantes = int(bloqueado_hasta - now) + 1
        return redirect(f"/?error=bloqueado&segundos={segundos_restantes}")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    exito = False

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre, contrasena FROM usuario WHERE correo = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["contrasena"], password):
            exito = True
        else:
            intentos += 1
            session["login_attempts"] = intentos
            if intentos >= MAX_LOGIN_ATTEMPTS:
                session["login_locked_until"] = now + LOGIN_LOCKOUT_SECONDS
                session["login_attempts"] = 0
                return redirect(f"/?error=bloqueado&segundos={LOGIN_LOCKOUT_SECONDS}")
            return redirect(f"/?error=credenciales&intentos={MAX_LOGIN_ATTEMPTS - intentos}")

    except Error as error:
        print(error)
        return f"Error MySQL: {error}", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "connection" in locals() and connection.is_connected(): connection.close()

    if not exito:
        return redirect("/?error=credenciales")

    session["logueado"] = True
    session["usuario_id"] = user["id"]
    session["nombre"] = user["nombre"]
    session["admin"] = (email == ADMIN_EMAIL)
    session["login_attempts"] = 0
    session["login_locked_until"] = 0

    if session["admin"]:
        return redirect("/admin?login=success")

    return redirect("/dashboard?login=success")


@app.route("/dashboard")
def dashboard():
    """Sirve web/index.html (dashboard con productos destacados). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")
    return send_from_directory(SITE_DIR, "index.html")

@app.route("/productos")
def productos():
    """Sirve web/productos.html (catálogo completo). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")
    return send_from_directory(SITE_DIR, "productos.html")

@app.route("/producto/<int:producto_id>")
def producto_detalle(producto_id):
    """Sirve web/producto.html (detalle de producto). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")
    return send_from_directory(SITE_DIR, "producto.html")

@app.route("/api/producto/<int:producto_id>")
def api_producto(producto_id):
    """Retorna JSON de un producto individual desde la BD."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM producto WHERE id = %s", (producto_id,))
        row = cursor.fetchone()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()
    if not row:
        return {"error": "No encontrado"}, 404
    return producto_db_a_dict(row)

@app.route("/api/productos")
def api_productos():
    """Retorna JSON con todos los productos ordenados por id."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM producto ORDER BY id")
        rows = cursor.fetchall()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()
    return [producto_db_a_dict(r) for r in rows]

@app.route("/usuario")
def usuario():
    """Retorna JSON con id, nombre, email y admin del usuario logueado."""

    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    email = ""
    usuario_id = session.get("usuario_id")
    if usuario_id:
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT correo FROM usuario WHERE id = %s", (usuario_id,))
            row = cursor.fetchone()
            if row:
                email = row["correo"]
        except Error:
            pass
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

    return {
        "id": session.get("usuario_id"),
        "nombre": session.get("nombre", ""),
        "email": email,
        "admin": session.get("admin", False)
    }

# ===== GESTIÓN DE CUENTA =====

@app.route("/api/usuario/editar", methods=["POST"])
def api_editar_usuario():
    """Actualiza nombre y correo del usuario logueado. Verifica que el correo no esté en uso."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    data = request.get_json()
    if not data:
        return {"error": "Datos inválidos"}, 400

    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip().lower()
    usuario_id = session["usuario_id"]

    if len(nombre) < 3:
        return {"error": "Nombre inválido"}, 400
    if "@" not in email:
        return {"error": "Correo inválido"}, 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM usuario WHERE correo = %s AND id != %s", (email, usuario_id))
        if cursor.fetchone():
            return {"error": "El correo ya está en uso"}, 400

        cursor.execute("UPDATE usuario SET nombre = %s, correo = %s WHERE id = %s", (nombre, email, usuario_id))
        connection.commit()

        session["nombre"] = nombre
        session["admin"] = (email == ADMIN_EMAIL)

        return {"ok": True}
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

@app.route("/api/usuario/cambiar-contrasena", methods=["POST"])
def api_cambiar_contrasena():
    """Cambia la contraseña del usuario verificando la actual primero."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    data = request.get_json()
    if not data:
        return {"error": "Datos inválidos"}, 400

    actual = data.get("actual", "")
    nueva = data.get("nueva", "")
    usuario_id = session["usuario_id"]

    if len(nueva) < 8:
        return {"error": "La nueva contraseña debe tener mínimo 8 caracteres"}, 400

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT contrasena FROM usuario WHERE id = %s", (usuario_id,))
        user = cursor.fetchone()

        if not user:
            return {"error": "Usuario no encontrado"}, 404

        if not check_password_hash(user["contrasena"], actual):
            return {"error": "La contraseña actual es incorrecta"}, 400

        nueva_hash = generate_password_hash(nueva)
        cursor.execute("UPDATE usuario SET contrasena = %s WHERE id = %s", (nueva_hash, usuario_id))
        connection.commit()

        return {"ok": True}
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

@app.route("/api/usuario/eliminar", methods=["POST"])
def api_eliminar_usuario():
    """Elimina la cuenta del usuario y todos sus pedidos asociados."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    usuario_id = session["usuario_id"]

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM detalle_pedido WHERE pedido_id IN (SELECT id FROM pedido WHERE usuario_id = %s)", (usuario_id,))
        cursor.execute("DELETE FROM pedido WHERE usuario_id = %s", (usuario_id,))
        cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))
        connection.commit()

        return {"ok": True}
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

# ===== CHECKOUT Y PAGOS =====

# Stripe ya está importado arriba

@app.route("/checkout")
def checkout():
    """Sirve web/checkout.html (página de pago con Stripe). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")

    return send_from_directory(SITE_DIR, "checkout.html")

@app.route("/pedido-exitoso")
def pedido_exitoso():
    """Sirve web/pedido-exitoso.html (confirmación de pago). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")

    return send_from_directory(SITE_DIR, "pedido-exitoso.html")

@app.route("/pedido-fallido")
def pedido_fallido():
    """Sirve web/pedido-fallido.html (pago rechazado). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")

    return send_from_directory(SITE_DIR, "pedido-fallido.html")

@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    """Crea PaymentIntent en Stripe + pedido en BD con items y descuento de stock."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    data = request.get_json()
    if not data:
        return {"error": "Datos inválidos"}, 400

    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    telefono = data.get("telefono", "").strip()
    direccion = data.get("direccion", "").strip()
    items_data = data.get("items", [])

    if not nombre or not email or not items_data:
        return {"error": "Campos obligatorios faltantes"}, 400

    referencia = f"APOMAT-{int(time.time())}-{session.get('usuario_id', 0)}-{random.randint(1000,9999)}"

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        total_calculado = 0
        costo_envio = 0
        items_validados = []

        for item in items_data:
            cursor.execute("SELECT id, precio, precio_rebaja, stock, nombre FROM producto WHERE id = %s AND disponible = 1", (item["id"],))
            prod = cursor.fetchone()
            if not prod:
                return {"error": f"Producto ID {item['id']} no encontrado o no disponible"}, 400
            precio_real = prod["precio_rebaja"] if prod["precio_rebaja"] and prod["precio_rebaja"] > 0 else prod["precio"]
            cantidad = int(item.get("cantidad", 1))
            if cantidad < 1:
                cantidad = 1
            if prod["stock"] < cantidad:
                return {"error": f"Stock insuficiente para {prod['nombre']}"}, 400
            subtotal = precio_real * cantidad
            total_calculado += subtotal
            items_validados.append({"id": prod["id"], "precio": precio_real, "cantidad": cantidad})

        costo_envio = 0 if total_calculado >= 150000 else 5000
        total_con_envio = total_calculado + costo_envio
        total_centavos = total_con_envio * 100

        payment_intent = stripe.PaymentIntent.create(
            amount=total_centavos,
            currency="cop",
            metadata={"referencia": referencia, "usuario_id": str(session.get("usuario_id", ""))},
            automatic_payment_methods={"enabled": True},
        )

        cursor = connection.cursor(dictionary=False)
        cursor.execute("""
            INSERT INTO pedido (usuario_id, referencia, total, costo_envio, estado, nombre, email, telefono, direccion)
            VALUES (%s, %s, %s, %s, 'pendiente', %s, %s, %s, %s)
        """, (session.get("usuario_id"), referencia, total_con_envio, costo_envio, nombre, email, telefono, direccion))
        pedido_id = cursor.lastrowid

        for item in items_validados:
            cursor.execute("""
                INSERT INTO detalle_pedido (pedido_id, producto_id, nombre_producto, precio, cantidad)
                VALUES (%s, %s, (SELECT nombre FROM producto WHERE id = %s), (SELECT COALESCE(precio_rebaja, precio) FROM producto WHERE id = %s), %s)
            """, (pedido_id, item["id"], item["id"], item["id"], item["cantidad"]))
            cursor.execute("UPDATE producto SET stock = stock - %s WHERE id = %s AND stock >= %s",
                           (item["cantidad"], item["id"], item["cantidad"]))

        connection.commit()

    except Error as error:
        if "connection" in locals() and connection.is_connected():
            connection.rollback()
        return {"error": "Error al procesar el pedido"}, 500
    except stripe.error.StripeError as e:
        if "connection" in locals() and connection.is_connected():
            connection.rollback()
        return {"error": "Error al procesar el pago"}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return {"ok": True, "client_secret": payment_intent.client_secret, "referencia": referencia, "payment_intent_id": payment_intent.id}

@app.route("/api/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Escucha webhook payment_intent.succeeded de Stripe y actualiza estado del pedido."""
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return {"error": "Firma inválida"}, 400

    if event["type"] == "payment_intent.succeeded":
        intent_data = event["data"]["object"]
        referencia = intent_data.get("metadata", {}).get("referencia")
        if referencia:
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("UPDATE pedido SET estado = 'confirmado' WHERE referencia = %s", (referencia,))
                connection.commit()
            except Error as error:
                print(f"Error webhook Stripe: {error}")
            finally:
                if "cursor" in locals():
                    cursor.close()
                if "connection" in locals() and connection.is_connected():
                    connection.close()

    return {"ok": True}

# ===== PEDIDOS DEL USUARIO =====
@app.route("/mis-pedidos")
def mis_pedidos():
    """Sirve web/mis-pedidos.html (historial de pedidos del usuario). Requiere sesión."""
    if "logueado" not in session:
        return redirect("/")

    return send_from_directory(SITE_DIR, "mis-pedidos.html")

@app.route("/api/mis-pedidos")
def api_mis_pedidos():
    """Retorna JSON con los pedidos del usuario logueado, cada uno con sus items."""
    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    usuario_id = session.get("usuario_id")
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, referencia, total, costo_envio, estado, fecha
            FROM pedido
            WHERE usuario_id = %s
            ORDER BY fecha DESC
        """, (usuario_id,))
        pedidos = cursor.fetchall()
        for pedido in pedidos:
            cursor.execute("""
                SELECT nombre_producto, precio, cantidad
                FROM detalle_pedido
                WHERE pedido_id = %s
            """, (pedido["id"],))
            pedido["items"] = cursor.fetchall()
            if pedido["items"]:
                pedido["total_items"] = sum(i["precio"] * i["cantidad"] for i in pedido["items"])
            pedido["fecha"] = pedido["fecha"].isoformat() if pedido["fecha"] else None
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return pedidos

@app.route("/admin/api/pedidos/estado/<int:pedido_id>", methods=["POST"])
def admin_actualizar_estado(pedido_id):
    """Cambia el estado de un pedido (admin only). Estados válidos: pendiente, enviado, entregado, cancelado."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    nuevo_estado = request.form.get("estado", "").strip()
    estados_validos = {"pendiente", "enviado", "entregado", "cancelado"}
    if nuevo_estado not in estados_validos:
        return {"error": "Estado inv\u00e1lido"}, 400

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE pedido SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
        connection.commit()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return {"ok": True}

@app.route("/enviar-contacto", methods=["POST"])
def enviar_contacto():
    """Guarda mensaje del formulario de contacto en BD y redirige."""
    if "logueado" not in session:
        return redirect("/")

    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip().lower()
    mensaje = request.form.get("mensaje", "").strip()

    redirect_url = request.referrer or "/dashboard"

    if not nombre or not email or not mensaje:
        return redirect(redirect_url.split("?")[0] + "?contacto=error")

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacto (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) NOT NULL,
                mensaje TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        query = """
        INSERT INTO contacto (nombre, correo, mensaje)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (nombre, email, mensaje))
        connection.commit()

    except Error as error:
        print(error)

    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return redirect(redirect_url.split("?")[0] + "?contacto=exito")

# ===== PANEL DE ADMINISTRACIÓN =====

@app.route("/admin")
def admin_panel():
    """Sirve web/admin.html (panel de administración). Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return redirect("/dashboard")

    return send_from_directory(SITE_DIR, "admin.html")

@app.route("/admin/api/productos")
def admin_api_productos():
    """Retorna JSON con todos los productos para el panel admin. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM producto ORDER BY id")
        rows = cursor.fetchall()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return [producto_db_a_dict(r) for r in rows]

@app.route("/admin/productos/agregar", methods=["POST"])
def admin_agregar_producto():
    """Crea un nuevo producto con imagen subida. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "0").strip()
    descripcion = request.form.get("descripcion", "").strip()
    precio_rebaja = request.form.get("precio_rebaja", "").strip()
    disponible = 1 if request.form.get("disponible") == "on" else 0
    stock = request.form.get("stock", "0").strip()

    if not nombre:
        return redirect("/admin?error=campos")

    try:
        precio = int(precio.replace(".", ""))
        precio_rebaja = int(precio_rebaja.replace(".", "")) if precio_rebaja else None
        stock = int(stock)
    except ValueError:
        return redirect("/admin?error=precio")

    caracteristicas_raw = request.form.get("caracteristicas", "").strip()
    especificaciones_raw = request.form.get("especificaciones", "").strip()

    caracteristicas = json.dumps([c.strip() for c in caracteristicas_raw.split("\n") if c.strip()])
    especificaciones = json.dumps([e.strip() for e in especificaciones_raw.split("\n") if e.strip()])

    imagen = "img-1.png"
    if "imagen" in request.files:
        file = request.files["imagen"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            # nombre único
            unique = f"prod_{int(time.time())}_{filename}"
            file.save(str(SITE_DIR / "img" / unique))
            imagen = unique

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO producto (nombre, imagen, precio, descripcion, caracteristicas, especificaciones, disponible, precio_rebaja, stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, imagen, precio, descripcion, caracteristicas, especificaciones, disponible, precio_rebaja, stock))
        connection.commit()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return redirect("/admin?ok=agregado")

@app.route("/admin/api/pedidos")
def admin_api_pedidos():
    """Retorna JSON con todos los pedidos y sus items. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.referencia, p.total, p.costo_envio, p.estado, p.nombre, p.email, p.telefono,
                   p.direccion, p.fecha, u.nombre AS usuario_nombre
            FROM pedido p
            LEFT JOIN usuario u ON p.usuario_id = u.id
            ORDER BY p.fecha DESC
        """)
        pedidos = cursor.fetchall()

        for pedido in pedidos:
            cursor.execute("""
                SELECT nombre_producto, precio, cantidad
                FROM detalle_pedido
                WHERE pedido_id = %s
            """, (pedido["id"],))
            pedido["items"] = cursor.fetchall()

    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return pedidos

@app.route("/admin/api/dashboard")
def admin_api_dashboard():
    """Retorna estadísticas del dashboard. Acepta ?mes=YYYY-MM para filtrar por mes."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    mes_filtro = request.args.get("mes", "").strip()
    where_mes = ""
    if mes_filtro:
        where_mes = " AND DATE_FORMAT(fecha, '%Y-%m') = %s "

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Globales (sin filtro de mes)
        cursor.execute("SELECT COUNT(*) AS total FROM usuario")
        total_usuarios = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM producto")
        total_productos = cursor.fetchone()["total"]

        # Pedidos totales
        sql_base = "FROM pedido WHERE estado != 'cancelado'"
        params_base = []
        if mes_filtro:
            sql_base += " AND DATE_FORMAT(fecha, '%Y-%m') = %s"
            params_base.append(mes_filtro)
        cursor.execute(f"SELECT COUNT(*) AS total, COALESCE(SUM(total),0) AS monto, COALESCE(SUM(costo_envio),0) AS envios {sql_base}", params_base)
        row = cursor.fetchone()
        total_pedidos = row["total"]
        ventas_totales = row["monto"]
        costo_envio_total = row["envios"]

        cursor.execute(f"SELECT estado, COUNT(*) AS cantidad {sql_base} GROUP BY estado", params_base)
        pedidos_por_estado = {}
        for r in cursor.fetchall():
            pedidos_por_estado[r["estado"]] = r["cantidad"]

        cursor.execute(f"SELECT COALESCE(SUM(dp.cantidad),0) AS total, COALESCE(SUM(dp.precio * dp.cantidad),0) AS ingresos FROM detalle_pedido dp JOIN pedido p ON dp.pedido_id = p.id WHERE p.estado != 'cancelado'", [])
        if mes_filtro:
            cursor.execute(f"SELECT COALESCE(SUM(dp.cantidad),0) AS total, COALESCE(SUM(dp.precio * dp.cantidad),0) AS ingresos FROM detalle_pedido dp JOIN pedido p ON dp.pedido_id = p.id WHERE p.estado != 'cancelado' AND DATE_FORMAT(p.fecha, '%Y-%m') = %s", (mes_filtro,))
        row = cursor.fetchone()
        unidades_vendidas = row["total"]
        ingresos_brutos = row["ingresos"]

        # Ventas mensuales últimos 12 meses
        cursor.execute("""
            SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes, COUNT(*) AS pedidos, COALESCE(SUM(total),0) AS ventas, COALESCE(SUM(costo_envio),0) AS envios
            FROM pedido WHERE estado != 'cancelado' AND fecha >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha, '%Y-%m') ORDER BY mes
        """)
        ventas_mensuales = cursor.fetchall()

        # Productos más vendidos (con o sin filtro de mes)
        sql_top = "SELECT dp.nombre_producto, SUM(dp.cantidad) AS total_vendido, COALESCE(SUM(dp.precio * dp.cantidad),0) AS total_ingresos FROM detalle_pedido dp JOIN pedido p ON dp.pedido_id = p.id WHERE p.estado != 'cancelado'"
        params_top = []
        if mes_filtro:
            sql_top += " AND DATE_FORMAT(p.fecha, '%Y-%m') = %s"
            params_top.append(mes_filtro)
        sql_top += " GROUP BY dp.nombre_producto ORDER BY total_vendido DESC LIMIT 5"
        cursor.execute(sql_top, params_top)
        productos_mas_vendidos = cursor.fetchall()

        # Pedidos recientes
        sql_recent = "SELECT p.id, p.referencia, p.total, p.estado, p.fecha, u.nombre AS cliente FROM pedido p LEFT JOIN usuario u ON p.usuario_id = u.id WHERE 1=1"
        params_recent = []
        if mes_filtro:
            sql_recent += " AND DATE_FORMAT(p.fecha, '%Y-%m') = %s"
            params_recent.append(mes_filtro)
        sql_recent += " ORDER BY p.fecha DESC LIMIT 8"
        cursor.execute(sql_recent, params_recent)
        pedidos_recientes = cursor.fetchall()
        for pr in pedidos_recientes:
            if pr["fecha"]:
                pr["fecha"] = pr["fecha"].isoformat()

        # Meses disponibles para el selector
        cursor.execute("SELECT DISTINCT DATE_FORMAT(fecha, '%Y-%m') AS mes FROM pedido ORDER BY mes DESC")
        meses_disponibles = [r["mes"] for r in cursor.fetchall() if r["mes"]]

        promedio_pedido = round(ventas_totales / total_pedidos, 0) if total_pedidos > 0 else 0

        return {
            "total_usuarios": total_usuarios,
            "total_productos": total_productos,
            "total_pedidos": total_pedidos,
            "ventas_totales": ventas_totales,
            "costo_envio_total": costo_envio_total,
            "ingresos_brutos": ingresos_brutos,
            "unidades_vendidas": unidades_vendidas,
            "promedio_pedido": promedio_pedido,
            "pedidos_por_estado": pedidos_por_estado,
            "ventas_mensuales": ventas_mensuales,
            "productos_mas_vendidos": productos_mas_vendidos,
            "pedidos_recientes": pedidos_recientes,
            "meses_disponibles": meses_disponibles,
            "mes_actual": mes_filtro or "todas",
        }
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "connection" in locals() and connection.is_connected(): connection.close()

@app.route("/admin/productos/toggle/<int:producto_id>", methods=["POST"])
def admin_toggle_producto(producto_id):
    """Activa/desactiva la disponibilidad de un producto. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    disponible = request.form.get("disponible")
    if disponible is not None:
        nuevo = 1 if disponible == "1" else 0
    else:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT disponible FROM producto WHERE id = %s", (producto_id,))
            row = cursor.fetchone()
            if not row:
                return {"error": "No encontrado"}, 404
            nuevo = 0 if row[0] else 1
        except Error as error:
            return {"error": str(error)}, 500
        finally:
            if "cursor" in locals(): cursor.close()
            if "connection" in locals() and connection.is_connected(): connection.close()

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE producto SET disponible = %s WHERE id = %s", (nuevo, producto_id))
        connection.commit()
        return {"ok": True, "disponible": bool(nuevo)}
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

@app.route("/admin/productos/editar/<int:producto_id>", methods=["POST"])
def admin_editar_producto(producto_id):
    """Edita precio, precio_rebaja y stock de un producto. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return {"error": "No autorizado"}, 401

    precio = request.form.get("precio", "").strip()
    precio_rebaja = request.form.get("precio_rebaja", "").strip()
    stock = request.form.get("stock", "").strip()

    try:
        precio = int(precio.replace(".", ""))
        precio_rebaja = int(precio_rebaja.replace(".", "")) if precio_rebaja else None
        stock = int(stock) if stock else None
    except ValueError:
        return redirect("/admin?error=precio")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        if stock is not None:
            cursor.execute("UPDATE producto SET precio = %s, precio_rebaja = %s, stock = %s WHERE id = %s",
                           (precio, precio_rebaja, stock, producto_id))
        else:
            cursor.execute("UPDATE producto SET precio = %s, precio_rebaja = %s WHERE id = %s",
                           (precio, precio_rebaja, producto_id))
        connection.commit()
    except Error as error:
        return {"error": str(error)}, 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return redirect("/admin?ok=editado")

@app.route("/admin/productos/eliminar/<int:producto_id>", methods=["POST"])
def admin_eliminar_producto(producto_id):
    """Elimina un producto y su archivo de imagen del servidor. Solo admin."""
    if "logueado" not in session or not session.get("admin"):
        return redirect("/dashboard")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT imagen FROM producto WHERE id = %s", (producto_id,))
        row = cursor.fetchone()
        if row:
            imagen = row[0]
            ruta_imagen = SITE_DIR / "img" / imagen
            if ruta_imagen.exists():
                ruta_imagen.unlink()
        cursor.execute("UPDATE detalle_pedido SET producto_id = NULL WHERE producto_id = %s", (producto_id,))
        cursor.execute("DELETE FROM producto WHERE id = %s", (producto_id,))
        connection.commit()
    except Error as error:
        print(error)
        connection.rollback()
        return redirect("/admin?error=eliminar_fk")
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return redirect("/admin?ok=eliminado")

@app.route("/enviar-codigo", methods=["POST"])
def enviar_codigo():
    """Genera un código de verificación y lo almacena en sesión."""
    email = request.form.get("email", "").strip().lower()
    if not email or "@" not in email:
        return redirect("/?error=recuperar_email")
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM usuario WHERE correo = %s", (email,))
        user = cursor.fetchone()
    except Error as error:
        return redirect("/?error=recuperar_error")
    finally:
        if "cursor" in locals(): cursor.close()
        if "connection" in locals() and connection.is_connected(): connection.close()
    if not user:
        return redirect("/?error=recuperar_no_existe")

    codigo = str(random.randint(100000, 999999))
    session["codigo_recuperacion"] = codigo
    session["codigo_email"] = email
    session["codigo_expira"] = time.time() + 600  # 10 minutos

    return redirect(f"/?codigo_enviado=ok&codigo={codigo}&email={email}")

@app.route("/verificar-codigo", methods=["POST"])
def verificar_codigo():
    """Verifica el código y cambia la contraseña."""
    email = request.form.get("email", "").strip().lower()
    codigo = request.form.get("codigo", "").strip()
    nueva = request.form.get("password", "")

    if not codigo:
        return redirect(f"/?error=codigo_vacio&email={email}")
    if len(nueva) < 8:
        return redirect(f"/?error=recuperar_corta&email={email}")

    almacenado = session.get("codigo_recuperacion")
    email_sesion = session.get("codigo_email")
    expira = session.get("codigo_expira", 0)

    if not almacenado or email != email_sesion:
        return redirect(f"/?error=codigo_invalido&email={email}")
    if time.time() > expira:
        session.pop("codigo_recuperacion", None)
        session.pop("codigo_email", None)
        session.pop("codigo_expira", None)
        return redirect(f"/?error=codigo_expirado&email={email}")
    if codigo != almacenado:
        return redirect(f"/?error=codigo_incorrecto&email={email}")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        nueva_hash = generate_password_hash(nueva)
        cursor.execute("UPDATE usuario SET contrasena = %s WHERE correo = %s", (nueva_hash, email))
        connection.commit()
    except Error as error:
        return redirect("/?error=recuperar_error")
    finally:
        if "cursor" in locals(): cursor.close()
        if "connection" in locals() and connection.is_connected(): connection.close()

    session.pop("codigo_recuperacion", None)
    session.pop("codigo_email", None)
    session.pop("codigo_expira", None)
    return redirect("/?recuperacion=exito")

@app.route("/logout")
def logout():
    """Limpia la sesión y redirige al login con headers sin caché."""
    session.clear()

    response = redirect("/")

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# ejecutar la app
if __name__ == "__main__":

    inicializar_base_datos()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
