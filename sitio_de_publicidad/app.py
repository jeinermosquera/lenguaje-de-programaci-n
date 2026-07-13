# app.py - aplicación principal de Flask para el proyecto de login
from pathlib import Path
from flask import Flask, redirect, request, send_from_directory, session

# para conectar con la base de datos MySQL
import mysql.connector
from mysql.connector import Error

# encripta las contraseñas y verifica las contraseñas en el login
from werkzeug.security import generate_password_hash, check_password_hash

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

# obtener datos del usuario logueado
@app.route("/usuario")
def usuario():

    if "logueado" not in session:
        return {"error": "No autorizado"}, 401

    return {
        "nombre": session.get("nombre", "")
    }

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