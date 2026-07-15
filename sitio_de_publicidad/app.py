# app.py - aplicación principal de Flask para el proyecto de login
from pathlib import Path
from flask import Flask, redirect, request, send_from_directory, session

# para conectar con la base de datos MySQL
import mysql.connector
from mysql.connector import Error

# encripta las contraseñas y verifica las contraseñas en el login
from werkzeug.security import generate_password_hash, check_password_hash

# datos de productos (catálogo estático)
PRODUCTOS = {
    1: {
        "nombre": "Cofe Mocka",
        "imagen": "img-1.png",
        "precio": 20000,
        "descripcion": "Una fusión cálida y envolvente que combina las notas del café recién molido con el dulce abrazo del cacao. Ideal para crear ambientes acogedores en hogares y cafeterías.",
        "caracteristicas": [
            "Aroma intenso a café y chocolate",
            "Ideal para espacios cerrados",
            "Sensación de calidez y confort"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    2: {
        "nombre": "Mora azul",
        "imagen": "img-8.png",
        "precio": 20000,
        "descripcion": "Un aroma fresco y frutal que evoca los bosques montañosos de Colombia. Las notas dulces de la mora azul se combinan con un toque silvestre que revitaliza cualquier espacio.",
        "caracteristicas": [
            "Aroma frutal y fresco",
            "Revitaliza el ambiente",
            "Notas silvestres naturales"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    3: {
        "nombre": "Celeste Cotton",
        "imagen": "img-2.png",
        "precio": 20000,
        "descripcion": "Inspirado en la frescura del algodón recién lavado y el azul del cielo colombiano. Una fragancia limpia, suave y reconfortante que evoca la sensación de ropa secada al sol.",
        "caracteristicas": [
            "Aroma limpio y suave",
            "Sensación de frescura duradera",
            "Perfecto para habitaciones y roperos"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    4: {
        "nombre": "Sandía pasión",
        "imagen": "img-4.png",
        "precio": 20000,
        "descripcion": "La combinación perfecta entre la dulzura de la sandía y el toque exótico del maracuyá. Un aroma vibrante y tropical que transporta a las playas del Pacífico colombiano.",
        "caracteristicas": [
            "Aroma tropical vibrante",
            "Notas dulces y exóticas",
            "Energizante y refrescante"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    5: {
        "nombre": "Sabor maracuyá",
        "imagen": "img-1.png",
        "precio": 20000,
        "descripcion": "La esencia del maracuyá más dulce y tropical capturada en cada gota. Un aroma que despierta los sentidos y llena de energía cualquier espacio del hogar.",
        "caracteristicas": [
            "Aroma cítrico y dulce",
            "Estimulante y refrescante",
            "Notas tropicales auténticas"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    6: {
        "nombre": "Paloma natural",
        "imagen": "img-8.png",
        "precio": 20000,
        "descripcion": "Una fragancia floral y etérea que evoca la pureza y la tranquilidad. Las notas suaves de flores blancas se entrelazan para crear un ambiente de paz y serenidad.",
        "caracteristicas": [
            "Aroma floral suave",
            "Sensación de paz y serenidad",
            "Ideal para meditación y descanso"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": False
    },
    7: {
        "nombre": "Naturaleza kiwi",
        "imagen": "img-2.png",
        "precio": 20000,
        "descripcion": "Un aroma fresco y chispeante que captura la esencia del kiwi recién cortado. Perfecto para espacios que buscan una atmósfera vibrante y llena de vida natural.",
        "caracteristicas": [
            "Aroma fresco y frutal",
            "Notas verdes y vibrantes",
            "Energía natural para el hogar"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    },
    8: {
        "nombre": "Fresa carnaval",
        "imagen": "img-4.png",
        "precio": 20000,
        "descripcion": "La alegría del carnaval colombiano en un aroma. Las notas dulces y jugosas de la fresa se mezclan con un toque festivo que llena de color y energía cualquier ambiente.",
        "caracteristicas": [
            "Aroma dulce y festivo",
            "Notas jugosas de fresa",
            "Ambiente alegre y vibrante"
        ],
        "especificaciones": [
            "Presentación: 250 ml",
            "Duración aproximada: 30 días",
            "Difusor de varillas incluidas"
        ],
        "disponible": True
    }
}

# la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent

LOGIN_DIR = BASE_DIR / "login"
SITE_DIR = BASE_DIR / "web"
STATIC_DIR = BASE_DIR / "static"

# crear la app de Flask
app = Flask(__name__)
app.secret_key = "clave_super_secreta"



# evitar que el navegador guarde páginas en caché
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# función para obtener la conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="jeiner_db"
    )

# rutas para el html del login
@app.route("/")
def home():
    return send_from_directory(LOGIN_DIR, "index.html")

# rutas para el css del login
@app.route("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(LOGIN_DIR / "css", filename)

# ruta para imágenes del login (aquí va el logo)
@app.route("/img/<path:filename>")
def img_files(filename):
    return send_from_directory(LOGIN_DIR / "img", filename)

# ruta para archivos de favicon del login
@app.route("/favicon/<path:filename>")
def favicon_files(filename):
    return send_from_directory(LOGIN_DIR / "favicon", filename)

# ruta para css del sitio web (carpeta "web")
@app.route("/site/css/<path:filename>")
def site_css(filename):
    return send_from_directory(SITE_DIR / "css", filename)

# ruta para imágenes del sitio web
@app.route("/site/img/<path:filename>")
def site_img(filename):
    return send_from_directory(SITE_DIR / "img", filename)

# ruta para js del sitio web
@app.route("/site/js/<path:filename>")
def site_js(filename):
    return send_from_directory(SITE_DIR / "js", filename)

# ruta para archivos de favicon del sitio web
@app.route("/site/favicon/<path:filename>")
def site_favicon(filename):
    return send_from_directory(SITE_DIR / "favicon", filename)

# ruta para imágenes estáticas (opcional, si prefieres usar /static/img en vez de /img)
@app.route("/static/img/<path:filename>")
def static_img(filename):
    return send_from_directory(STATIC_DIR / "img", filename)

# registro de usuario
@app.route("/register", methods=["POST"])
def register():

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if len(full_name) < 3:
        return "Nombre inválido", 400

    if "@" not in email:
        return "Correo inválido", 400

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
    session["nombre"] = full_name

    return redirect("/dashboard?register=success")

# login de usuario
@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT id, nombre, contrasena
        FROM usuario
        WHERE correo = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if not user:
            return redirect("/?error=credenciales")

        if not check_password_hash(user["contrasena"], password):
            return redirect("/?error=credenciales")

    except Error as error:
        print(error)
        return f"Error MySQL: {error}", 500

    finally:
        if "cursor" in locals():
            cursor.close()

        if "connection" in locals() and connection.is_connected():
            connection.close()

    # guardar sesión
    session["logueado"] = True
    session["usuario_id"] = user["id"]
    session["nombre"] = user["nombre"]

    return redirect("/dashboard?login=success")


# ruta protegida
@app.route("/dashboard")
def dashboard():

    if "logueado" not in session:
        return redirect("/")

    print("Usuario autorizado")

    return send_from_directory(SITE_DIR, "index.html")

# ruta protegida para la página de productos
@app.route("/productos")
def productos():

    if "logueado" not in session:
        return redirect("/")

    return send_from_directory(SITE_DIR, "productos.html")

# ruta protegida para detalle de producto
@app.route("/producto/<int:producto_id>")
def producto_detalle(producto_id):

    if "logueado" not in session:
        return redirect("/")

    if producto_id not in PRODUCTOS:
        return "Producto no encontrado", 404

    return send_from_directory(SITE_DIR, "producto.html")

# ruta para obtener datos de un producto (API interna)
@app.route("/api/producto/<int:producto_id>")
def api_producto(producto_id):

    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    if producto_id not in PRODUCTOS:
        return {"error": "No encontrado"}, 404

    producto = dict(PRODUCTOS[producto_id])
    producto["id"] = producto_id
    producto["precio_formateado"] = f"$ {producto['precio']:,.0f}".replace(",", ".")

    return producto

# obtener datos del usuario logueado
@app.route("/usuario")
def usuario():

    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    return {
        "nombre": session.get("nombre", "")
    }

# ruta para enviar mensaje de contacto
@app.route("/enviar-contacto", methods=["POST"])
def enviar_contacto():

    if "logueado" not in session:
        return redirect("/")

    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip().lower()
    mensaje = request.form.get("mensaje", "").strip()

    # redirigir a la página anterior o al dashboard por defecto
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

# cerrar sesión
@app.route("/logout")
def logout():

    session.clear()

    response = redirect("/")

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# ejecutar la app
if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )