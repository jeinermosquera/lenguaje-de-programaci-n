import os, re
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

# ─── Config ──────────────────────────────────────────────────────────────

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'comunidad-info-secret-key-2024')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'comunidad-info')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'informa@gmail.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '12345678')
    ADMIN_CODE = os.environ.get('ADMIN_CODE', 'ADMIN-2024-SECRET')
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'

# ─── DB ──────────────────────────────────────────────────────────────────

def get_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME,
            port=Config.DB_PORT
        )
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    conn = cursor = None
    try:
        conn = get_connection()
        if conn is None: return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch: return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid if cursor.lastrowid else True
    except Error as e:
        print(f"Error en base de datos: {e}")
        if conn: conn.rollback()
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



# ─── Auth Decorator ──────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login.login_page'))
        if session.get('rol') != 'admin':
            return redirect(url_for('user.user_home'))
        return f(*args, **kwargs)
    return decorated_function

# ─── Blueprints ──────────────────────────────────────────────────────────

from flask import Blueprint
login_bp = Blueprint('login', __name__, template_folder='login/templates', static_folder='login', static_url_path='/login')
inicio_bp = Blueprint('inicio', __name__, template_folder='web/inicio/templates', static_folder='web/inicio', static_url_path='/inicio')
user_bp = Blueprint('user', __name__, template_folder='web/user/templates', static_folder='web/user', static_url_path='/user')
admin_bp = Blueprint('admin', __name__, template_folder='admin/templates', static_folder='admin', static_url_path='/admin')

# ─── Login Model ─────────────────────────────────────────────────────────

def crear_usuario(nombre, apellido, correo, contrasena_hash, rol='usuario'):
    return execute_query(
        "INSERT INTO usuario (nombre, apellido, correo, contrasena, rol) VALUES (%s, %s, %s, %s, %s)",
        (nombre, apellido, correo, contrasena_hash, rol))

def obtener_usuario_por_correo(correo):
    result = execute_query("SELECT * FROM usuario WHERE correo = %s", (correo,), fetch=True)
    return result[0] if result else None

def obtener_usuario_por_id(user_id):
    result = execute_query("SELECT * FROM usuario WHERE id = %s", (user_id,), fetch=True)
    return result[0] if result else None

def actualizar_usuario(user_id, nombre, apellido, descripcion):
    return execute_query("UPDATE usuario SET nombre = %s, apellido = %s, descripcion = %s WHERE id = %s",
                         (nombre, apellido, descripcion, user_id))

def actualizar_fotografia(user_id, filename):
    return execute_query("UPDATE usuario SET fotografia = %s WHERE id = %s", (filename, user_id))

def obtener_todos_usuarios():
    return execute_query(
        "SELECT id, nombre, apellido, correo, rol, fotografia, descripcion, fecha_registro FROM usuario ORDER BY fecha_registro DESC",
        fetch=True) or []

def actualizar_rol_usuario(user_id, nuevo_rol):
    return execute_query("UPDATE usuario SET rol = %s WHERE id = %s", (nuevo_rol, user_id))

def eliminar_usuario_por_id(user_id):
    return execute_query("DELETE FROM usuario WHERE id = %s", (user_id,))

# ─── Login Controller ───────────────────────────────────────────────────

def validar_correo(correo):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo) is not None

def registrar_usuario(nombre, apellido, correo, contrasena, admin_code=None):
    if not nombre or not apellido or not correo or not contrasena:
        return False, "Todos los campos son obligatorios."
    if not validar_correo(correo):
        return False, "El formato del correo no es v\u00e1lido."
    if len(contrasena) < 6:
        return False, "La contrase\u00f1a debe tener al menos 6 caracteres."
    if obtener_usuario_por_correo(correo):
        return False, "Este correo ya est\u00e1 registrado."
    rol = 'admin' if admin_code and admin_code == Config.ADMIN_CODE else 'usuario'
    if admin_code and admin_code != Config.ADMIN_CODE:
        return False, "C\u00f3digo de administrador incorrecto."
    result = crear_usuario(nombre, apellido, correo, generate_password_hash(contrasena), rol)
    if result:
        return True, ("Registro de administrador exitoso." if rol == 'admin' else "Registro exitoso. Ahora puedes iniciar sesi\u00f3n.")
    return False, "Error al registrar. Intenta de nuevo."

def iniciar_sesion(correo, contrasena):
    if not correo or not contrasena:
        return False, "Correo y contrase\u00f1a son obligatorios."
    usuario = obtener_usuario_por_correo(correo)
    if not usuario or not check_password_hash(usuario['contrasena'], contrasena):
        return False, "Correo o contrase\u00f1a incorrectos."
    session['id'] = usuario['id']
    session['nombre'] = usuario['nombre']
    session['correo'] = usuario['correo']
    session['logueado'] = True
    session['rol'] = usuario.get('rol', 'usuario')
    return True, "Inicio de sesi\u00f3n exitoso."

# ─── Categories ──────────────────────────────────────────────────────────

CATEGORIAS_NOTICIAS = ['General', 'Deportes', 'Cultura', 'Educacion', 'Salud', 'Tecnologia', 'Politica']
CATEGORIAS_EVENTOS = ['General', 'Reunion', 'Taller', 'Cultural', 'Deportivo', 'Social', 'Capacitacion']

def build_categoria_filter(categoria, tabla='p'):
    if not categoria: return '', []
    return f" AND {tabla}.categoria = %s", [categoria]

def build_fecha_parts_filter(anio, mes, dia, columna):
    conds, params = '', []
    if anio:
        conds += f" AND YEAR({columna}) = %s"
        params.append(int(anio))
    if mes:
        conds += f" AND MONTH({columna}) = %s"
        params.append(int(mes))
    if dia:
        conds += f" AND DAY({columna}) = %s"
        params.append(int(dia))
    return conds, params

# ─── Public Model ────────────────────────────────────────────────────────

def ultimas_publicaciones(limite=10, categoria=None, anio=None, mes=None, dia=None):
    c1, p1 = build_categoria_filter(categoria)
    c2, p2 = build_fecha_parts_filter(anio, mes, dia, 'p.fecha_publicacion')
    q = f"""SELECT p.*, u.nombre, u.apellido, u.fotografia FROM publicaciones p
           JOIN usuario u ON p.usuario_id = u.id WHERE 1=1{c1}{c2} ORDER BY p.fecha_publicacion DESC LIMIT %s"""
    return execute_query(q, p1 + p2 + [limite], fetch=True) or []

def buscar_publicaciones(termino, categoria=None, anio=None, mes=None, dia=None):
    like = f"%{termino}%"
    c1, p1 = build_categoria_filter(categoria)
    c2, p2 = build_fecha_parts_filter(anio, mes, dia, 'p.fecha_publicacion')
    q = f"""SELECT p.*, u.nombre, u.apellido, u.fotografia FROM publicaciones p
           JOIN usuario u ON p.usuario_id = u.id
           WHERE (p.titulo LIKE %s OR p.contenido LIKE %s OR u.nombre LIKE %s OR u.apellido LIKE %s){c1}{c2}
           ORDER BY p.fecha_publicacion DESC"""
    return execute_query(q, [like, like, like, like] + p1 + p2, fetch=True) or []

def obtener_todas_publicaciones(categoria=None, anio=None, mes=None, dia=None):
    c1, p1 = build_categoria_filter(categoria)
    c2, p2 = build_fecha_parts_filter(anio, mes, dia, 'p.fecha_publicacion')
    q = f"""SELECT p.*, u.nombre, u.apellido, u.fotografia FROM publicaciones p
           JOIN usuario u ON p.usuario_id = u.id WHERE 1=1{c1}{c2} ORDER BY p.fecha_publicacion DESC"""
    return execute_query(q, p1 + p2, fetch=True) or []

def obtener_publicacion_por_id(pub_id):
    q = """SELECT p.*, u.nombre, u.apellido, u.fotografia FROM publicaciones p
           JOIN usuario u ON p.usuario_id = u.id WHERE p.id = %s"""
    result = execute_query(q, (pub_id,), fetch=True)
    return result[0] if result else None

def comentarios_por_publicacion(pub_id):
    q = """SELECT c.*, u.nombre, u.apellido, u.fotografia FROM comentarios c
           JOIN usuario u ON c.usuario_id = u.id WHERE c.publicacion_id = %s ORDER BY c.fecha_comentario ASC"""
    return execute_query(q, (pub_id,), fetch=True) or []

# ─── Admin Model ─────────────────────────────────────────────────────────

def crear_publicacion(usuario_id, titulo, contenido, categoria='General', imagen=None):
    return execute_query(
        "INSERT INTO publicaciones (usuario_id, titulo, contenido, categoria, imagen) VALUES (%s, %s, %s, %s, %s)",
        (usuario_id, titulo, contenido, categoria, imagen))

def actualizar_publicacion(pub_id, titulo, contenido, categoria, imagen=None):
    if imagen:
        return execute_query(
            "UPDATE publicaciones SET titulo=%s, contenido=%s, categoria=%s, imagen=%s WHERE id=%s",
            (titulo, contenido, categoria, imagen, pub_id))
    return execute_query(
        "UPDATE publicaciones SET titulo=%s, contenido=%s, categoria=%s WHERE id=%s",
        (titulo, contenido, categoria, pub_id))

def eliminar_publicacion(pub_id):
    execute_query("DELETE FROM comentarios WHERE publicacion_id = %s", (pub_id,))
    return execute_query("DELETE FROM publicaciones WHERE id = %s", (pub_id,))

def obtener_eventos_proximos(limite=12, categoria=None, anio=None, mes=None, dia=None):
    c1, p1 = build_categoria_filter(categoria, 'e')
    c2, p2 = build_fecha_parts_filter(anio, mes, dia, 'e.fecha_evento')
    base_cond = 'e.fecha_evento >= NOW()' if not (anio or mes or dia) else '1=1'
    q = f"""SELECT e.*, u.nombre, u.apellido FROM eventos e
           LEFT JOIN usuario u ON e.creado_por = u.id
           WHERE {base_cond}{c1}{c2} ORDER BY e.fecha_evento ASC LIMIT %s"""
    return execute_query(q, p1 + p2 + [limite], fetch=True) or []

def crear_evento(usuario_id, titulo, descripcion, fecha_evento, ubicacion, categoria, imagen):
    return execute_query(
        "INSERT INTO eventos (titulo, descripcion, fecha_evento, ubicacion, creado_por, categoria, imagen) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (titulo, descripcion, fecha_evento, ubicacion, usuario_id, categoria, imagen))

def actualizar_evento(evento_id, titulo, descripcion, fecha_evento, ubicacion, categoria, imagen):
    return execute_query(
        "UPDATE eventos SET titulo=%s, descripcion=%s, fecha_evento=%s, ubicacion=%s, categoria=%s, imagen=%s WHERE id=%s",
        (titulo, descripcion, fecha_evento, ubicacion, categoria, imagen, evento_id))

def eliminar_evento(evento_id):
    return execute_query("DELETE FROM eventos WHERE id = %s", (evento_id,))

def obtener_evento_por_id(evento_id):
    q = """SELECT e.*, u.nombre, u.apellido FROM eventos e
           LEFT JOIN usuario u ON e.creado_por = u.id WHERE e.id = %s"""
    result = execute_query(q, (evento_id,), fetch=True)
    return result[0] if result else None

# ─── Login Routes ────────────────────────────────────────────────────────

@login_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@inicio_bp.route('/inicio')
def landing():
    return render_template('landing.html')

def parse_fecha_params():
    a = request.args.get('anio', '').strip() or None
    m = request.args.get('mes', '').strip() or None
    d = request.args.get('dia', '').strip() or None
    return a, m, d

@login_bp.route('/api/publicas', methods=['GET'])
def publicas_list():
    termino = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    if termino:
        return jsonify({'success': True, 'data': buscar_publicaciones(termino, categoria, anio, mes, dia)})
    return jsonify({'success': True, 'data': ultimas_publicaciones(4, categoria, anio, mes, dia)})

@login_bp.route('/api/publicas/eventos', methods=['GET'])
def publicas_eventos():
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    return jsonify({'success': True, 'data': obtener_eventos_proximos(3, categoria, anio, mes, dia)})

@login_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    success, message = iniciar_sesion(data.get('correo', '').strip(), data.get('contrasena', ''))
    rol = session.get('rol', 'usuario') if success else None
    return jsonify({'success': success, 'message': message, 'rol': rol}), (200 if success else 401)

@login_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    success, message = registrar_usuario(
        data.get('nombre', '').strip(), data.get('apellido', '').strip(),
        data.get('correo', '').strip(), data.get('contrasena', ''),
        data.get('admin_code', '').strip() or None)
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@login_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Sesi\u00f3n cerrada.'})

# ─── User Routes ────────────────────────────────────────────────────────

@user_bp.route('/user/')
@login_required
def user_home():
    return render_template('home.html', nombre=session.get('nombre', 'Usuario'))

@user_bp.route('/user/eventos')
@login_required
def user_eventos():
    return render_template('eventos.html', nombre=session.get('nombre', 'Usuario'))

@user_bp.route('/user/publicacion/<int:pub_id>')
@login_required
def user_publicacion(pub_id):
    pub = obtener_publicacion_por_id(pub_id)
    if not pub: return redirect(url_for('user.user_home'))
    return render_template('publicacion.html', publicacion=pub)

@user_bp.route('/user/evento/<int:evento_id>')
@login_required
def user_evento(evento_id):
    ev = obtener_evento_por_id(evento_id)
    if not ev: return redirect(url_for('user.user_eventos'))
    return render_template('evento.html', evento=ev)

@user_bp.route('/api/user/publicaciones', methods=['GET'])
@login_required
def user_listar_publicaciones():
    termino = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    if termino:
        return jsonify({'success': True, 'data': buscar_publicaciones(termino, categoria, anio, mes, dia)})
    return jsonify({'success': True, 'data': obtener_todas_publicaciones(categoria, anio, mes, dia)})

@user_bp.route('/api/user/publicaciones/<int:pub_id>', methods=['GET'])
@login_required
def user_ver_publicacion(pub_id):
    pub = obtener_publicacion_por_id(pub_id)
    if not pub: return jsonify({'success': False, 'message': 'No encontrada.'}), 404
    pub['comentarios'] = comentarios_por_publicacion(pub_id)
    return jsonify({'success': True, 'data': pub})

@user_bp.route('/api/user/eventos', methods=['GET'])
@login_required
def user_listar_eventos():
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    return jsonify({'success': True, 'data': obtener_eventos_proximos(50, categoria, anio, mes, dia)})

@user_bp.route('/api/user/eventos/<int:evento_id>', methods=['GET'])
@login_required
def user_ver_evento(evento_id):
    ev = obtener_evento_por_id(evento_id)
    if not ev: return jsonify({'success': False, 'message': 'No encontrado.'}), 404
    return jsonify({'success': True, 'data': ev})

# ─── Admin Routes ──────────────────────────────────────────────────────

@admin_bp.route('/admin/')
@admin_required
def admin_dashboard():
    return render_template('dashboard.html', nombre=session.get('nombre', 'Admin'))

@admin_bp.route('/admin/noticias')
@admin_required
def admin_noticias():
    return render_template('noticias.html', nombre=session.get('nombre', 'Admin'))

@admin_bp.route('/admin/noticias/nueva')
@admin_required
def admin_noticia_nueva():
    return render_template('noticia_form.html', nombre=session.get('nombre', 'Admin'), noticia=None)

@admin_bp.route('/admin/noticias/<int:pub_id>/editar')
@admin_required
def admin_noticia_editar(pub_id):
    pub = obtener_publicacion_por_id(pub_id)
    if not pub: return redirect(url_for('admin.admin_noticias'))
    return render_template('noticia_form.html', nombre=session.get('nombre', 'Admin'), noticia=pub)

@admin_bp.route('/admin/eventos')
@admin_required
def admin_eventos():
    return render_template('eventos.html', nombre=session.get('nombre', 'Admin'))

@admin_bp.route('/admin/eventos/nuevo')
@admin_required
def admin_evento_nuevo():
    return render_template('evento_form.html', nombre=session.get('nombre', 'Admin'), evento=None)

@admin_bp.route('/admin/eventos/<int:ev_id>/editar')
@admin_required
def admin_evento_editar(ev_id):
    ev = obtener_evento_por_id(ev_id)
    if not ev: return redirect(url_for('admin.admin_eventos'))
    return render_template('evento_form.html', nombre=session.get('nombre', 'Admin'), evento=ev)

@admin_bp.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    return render_template('usuarios.html', nombre=session.get('nombre', 'Admin'))

# ─── Admin API ─────────────────────────────────────────────────────────

@admin_bp.route('/api/admin/publicaciones', methods=['GET'])
@admin_required
def admin_listar_publicaciones():
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    return jsonify({'success': True, 'data': obtener_todas_publicaciones(categoria, anio, mes, dia)})

@admin_bp.route('/api/admin/publicaciones', methods=['POST'])
@admin_required
def admin_crear_publicacion():
    data = request.get_json()
    rid = crear_publicacion(
        session['id'], data.get('titulo'), data.get('contenido'),
        data.get('categoria', 'General'), data.get('imagen'))
    if rid:
        return jsonify({'success': True, 'message': 'Publicacion creada.'}), 201
    return jsonify({'success': False, 'message': 'Error al crear.'}), 400

@admin_bp.route('/api/admin/publicaciones/<int:pub_id>', methods=['PUT'])
@admin_required
def admin_actualizar_publicacion(pub_id):
    data = request.get_json()
    ok = actualizar_publicacion(
        pub_id, data.get('titulo'), data.get('contenido'),
        data.get('categoria', 'General'), data.get('imagen'))
    if ok:
        return jsonify({'success': True, 'message': 'Publicacion actualizada.'})
    return jsonify({'success': False, 'message': 'Error al actualizar.'}), 400

@admin_bp.route('/api/admin/publicaciones/<int:pub_id>', methods=['DELETE'])
@admin_required
def admin_eliminar_publicacion(pub_id):
    ok = eliminar_publicacion(pub_id)
    if ok:
        return jsonify({'success': True, 'message': 'Publicacion eliminada.'})
    return jsonify({'success': False, 'message': 'Error al eliminar.'}), 400

@admin_bp.route('/api/admin/eventos', methods=['GET'])
@admin_required
def admin_listar_eventos():
    categoria = request.args.get('categoria', '').strip() or None
    anio, mes, dia = parse_fecha_params()
    return jsonify({'success': True, 'data': obtener_eventos_proximos(50, categoria, anio, mes, dia)})

@admin_bp.route('/api/admin/eventos', methods=['POST'])
@admin_required
def admin_crear_evento():
    data = request.get_json()
    rid = crear_evento(
        session['id'], data.get('titulo'), data.get('descripcion'),
        data.get('fecha_evento'), data.get('ubicacion'),
        data.get('categoria', 'General'), data.get('imagen'))
    if rid:
        return jsonify({'success': True, 'message': 'Evento creado.'}), 201
    return jsonify({'success': False, 'message': 'Error al crear.'}), 400

@admin_bp.route('/api/admin/eventos/<int:ev_id>', methods=['PUT'])
@admin_required
def admin_actualizar_evento(ev_id):
    data = request.get_json()
    ok = actualizar_evento(
        ev_id, data.get('titulo'), data.get('descripcion'),
        data.get('fecha_evento'), data.get('ubicacion'),
        data.get('categoria', 'General'), data.get('imagen'))
    if ok:
        return jsonify({'success': True, 'message': 'Evento actualizado.'})
    return jsonify({'success': False, 'message': 'Error al actualizar.'}), 400

@admin_bp.route('/api/admin/eventos/<int:ev_id>', methods=['DELETE'])
@admin_required
def admin_eliminar_evento(ev_id):
    ok = eliminar_evento(ev_id)
    if ok:
        return jsonify({'success': True, 'message': 'Evento eliminado.'})
    return jsonify({'success': False, 'message': 'Error al eliminar.'}), 400

@admin_bp.route('/api/admin/usuarios', methods=['GET'])
@admin_required
def admin_listar_usuarios():
    return jsonify({'success': True, 'data': obtener_todos_usuarios()})

@admin_bp.route('/api/admin/usuarios/<int:user_id>/rol', methods=['PUT'])
@admin_required
def admin_cambiar_rol(user_id):
    data = request.get_json()
    ok = actualizar_rol_usuario(user_id, data.get('rol'))
    if ok:
        return jsonify({'success': True, 'message': 'Rol actualizado.'})
    return jsonify({'success': False, 'message': 'Error.'}), 400

@admin_bp.route('/api/admin/usuarios/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_eliminar_usuario(user_id):
    ok = eliminar_usuario_por_id(user_id)
    if ok:
        return jsonify({'success': True, 'message': 'Usuario eliminado.'})
    return jsonify({'success': False, 'message': 'Error.'}), 400

# ─── DB Init ────────────────────────────────────────────────────────────

def init_database():
    conn = cursor = None
    try:
        conn = get_connection()
        if conn is None: return False
        cursor = conn.cursor()

        for col in [('publicaciones', 'categoria', "VARCHAR(50) DEFAULT 'General'"),
                    ('eventos', 'categoria', "VARCHAR(50) DEFAULT 'General'"),
                    ('eventos', 'imagen', "VARCHAR(500) DEFAULT NULL")]:
            cursor.execute(f"SHOW COLUMNS FROM {col[0]} LIKE '{col[1]}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE {col[0]} ADD COLUMN {col[1]} {col[2]}")
                conn.commit()
                print(f"Columna {col[1]} agregada a {col[0]}.")

        cursor.execute("SELECT id, rol FROM usuario WHERE correo = %s", (Config.ADMIN_EMAIL,))
        admin_row = cursor.fetchone()
        if admin_row:
            admin_id = admin_row[0]
            if admin_row[1] != 'admin':
                cursor.execute("UPDATE usuario SET rol = 'admin' WHERE id = %s", (admin_id,))
                conn.commit()
            admin_hash = generate_password_hash(Config.ADMIN_PASSWORD)
            cursor.execute("UPDATE usuario SET contrasena = %s WHERE id = %s", (admin_hash, admin_id))
            conn.commit()
        else:
            admin_hash = generate_password_hash(Config.ADMIN_PASSWORD)
            cursor.execute(
                "INSERT INTO usuario (nombre, apellido, correo, contrasena, rol) VALUES (%s, %s, %s, %s, %s)",
                ('Admin', 'Comunidad', Config.ADMIN_EMAIL, admin_hash, 'admin'))
            conn.commit()
            admin_id = cursor.lastrowid

        # ── 10 publicaciones ──
        cursor.execute("SELECT COUNT(*) FROM publicaciones")
        if cursor.fetchone()[0] < 10:
            noticias = [
                ('Bienvenidos a Comunidad Info', 'Esta es la primera publicacion de nuestra comunidad. Aqui encontraran las ultimas noticias, eventos y toda la informacion relevante para mantenerse al dia. Los invitamos a participar activamente compartiendo sus propias publicaciones y comentarios.', 'General', -30),
                ('Nuevo torneo deportivo', 'Se acerca el torneo anual de futbol y basquetbol. Inscripciones abiertas hasta el proximo mes. Participa con tu equipo y demuestra tu talento.', 'Deportes', -25),
                ('Taller de tecnologia para jovenes', 'Taller gratuito de programacion y robotica para jovenes de 12 a 18 años. Cupos limitados. Inscribite en el Centro de Innovacion.', 'Tecnologia', -20),
                ('Jornada de salud comunitaria', 'El centro de salud ofrecera controles gratuitos de presion, glucosa y vacunacion. Acercate de 8 a 14 hs.', 'Salud', -18),
                ('Exposicion de arte local', 'Artistas de la comunidad expondran sus obras en el Salon Cultural. Entrada libre y gratuita.', 'Cultura', -15),
                ('Charla sobre educacion financiera', 'Especialistas en finanzas personales brindaran consejos para ahorrar e invertir. No te lo pierdas.', 'Educacion', -12),
                ('Nueva ordenanza municipal', 'El concejo deliberante aprobo la nueva ordenanza de transito. Conoce los detalles y las nuevas normas.', 'Politica', -10),
                ('Concurso de fotografia urbana', 'Participa con tus mejores fotos de la ciudad. Premios para los primeros tres lugares.', 'Cultura', -8),
                ('Clases de apoyo escolar', 'La comunidad ofrece clases gratuitas de matematicas, lengua e ingles para nivel primario y secundario.', 'Educacion', -5),
                ('Campeonato de ajedrez', 'Inscripciones abiertas para el campeonato anual de ajedrez. Categorias infantil y adultos.', 'Deportes', -3),
            ]
            for t, c, cat, dias in noticias:
                fec = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO publicaciones (usuario_id, titulo, contenido, categoria, fecha_publicacion) VALUES (%s, %s, %s, %s, %s)",
                    (admin_id, t, c, cat, fec))
            conn.commit()
            print("10 publicaciones insertadas.")

        # ── Asignar imágenes a eventos existentes ──
        cursor.execute("UPDATE eventos SET imagen = %s WHERE imagen IS NULL AND id = %s", ('https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80', 1))
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM eventos WHERE imagen IS NULL")
        if cursor.fetchone()[0] > 0:
            urls = [
                'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80',
                'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80',
                'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80',
                'https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=800&q=80',
                'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80',
                'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&q=80',
                'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=800&q=80',
                'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80',
                'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80',
                'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&q=80',
            ]
            cursor.execute("SELECT id FROM eventos WHERE imagen IS NULL")
            rows = cursor.fetchall()
            for i, row in enumerate(rows):
                url = urls[i % len(urls)]
                cursor.execute("UPDATE eventos SET imagen = %s WHERE id = %s", (url, row[0]))
            conn.commit()
            print(f"{len(rows)} eventos actualizados con imagen.")

        # ── 10 eventos ──
        cursor.execute("SELECT COUNT(*) FROM eventos")
        if cursor.fetchone()[0] < 10:
            eventos = [
                ('Reunion comunitaria', 'Primera reunion abierta a toda la comunidad para compartir ideas y propuestas.', 15, 'Salon principal - Centro Comunitario', 'Reunion', 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80'),
                ('Torneo deportivo anual', 'Competencia de futbol, basquetbol y voleybol para todas las edades.', 30, 'Polideportivo Municipal', 'Deportivo', 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80'),
                ('Taller de programacion', 'Introduccion a Python y desarrollo web para principiantes.', 7, 'Centro de Innovacion', 'Taller', 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80'),
                ('Feria de ciencias', 'Estudiantes de todos los niveles presentaran sus proyectos cientificos y tecnologicos.', 45, 'Salon de Exposiciones', 'Cultural', 'https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=800&q=80'),
                ('Capacitacion en primeros auxilios', 'Curso intensivo de RCP y primeros auxilios. Certificacion oficial incluida.', 20, 'Centro de Salud', 'Capacitacion', 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80'),
                ('Cine al aire libre', 'Proyeccion de peliculas familiares en la plaza central. Lleva tu reposera.', 12, 'Plaza Central', 'Cultural', 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&q=80'),
                ('Jornada de limpieza urbana', 'Sumate a la jornada de limpieza y embellecimiento de nuestra ciudad.', 25, 'Punto de encuentro: Municipalidad', 'Social', 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=800&q=80'),
                ('Taller de huerta organica', 'Aprende a cultivar tus propios alimentos de manera organica y sostenible.', 18, 'Huerta Comunitaria', 'Taller', 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80'),
                ('Encuentro de emprendedores', 'Espacio para emprendedores locales. Exposicion, networking y capacitacion.', 35, 'Centro de Convenciones', 'Social', 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80'),
                ('Charla: Cuidado del medio ambiente', 'Conversatorio sobre practicas sostenibles y cuidado del entorno natural.', 10, 'Biblioteca Municipal', 'General', 'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&q=80'),
            ]
            for t, d, dias, ubi, cat, img in eventos:
                fec = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO eventos (titulo, descripcion, fecha_evento, ubicacion, creado_por, categoria, imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (t, d, fec, ubi, admin_id, cat, img))
            conn.commit()
            print("10 eventos insertados.")

        print("Base de datos verificada.")
        return True
    except Error as e:
        print(f"Error en base de datos: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ─── App Factory ─────────────────────────────────────────────────────────

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.static_folder = 'static'
    app.static_url_path = '/static'
    app.register_blueprint(login_bp)
    app.register_blueprint(inicio_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return redirect(url_for('inicio.landing'))

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'imagen' not in request.files:
            return jsonify({'success': False, 'message': 'No se envio ningun archivo.'}), 400
        file = request.files['imagen']
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'Archivo invalido.'}), 400
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Formato no permitido. Usa PNG, JPG, GIF, WebP o SVG.'}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        nombre = datetime.now().strftime('%Y%m%d%H%M%S%f') + '_' + str(hash(file.filename))[-6:] + '.' + ext
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        path = os.path.join(UPLOAD_FOLDER, nombre)
        file.save(path)
        url = '/static/uploads/' + nombre
        return jsonify({'success': True, 'url': url, 'message': 'Imagen subida.'})

    with app.app_context():
        init_database()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
