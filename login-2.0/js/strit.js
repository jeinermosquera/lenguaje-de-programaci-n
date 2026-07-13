// USUARIOS: guardar y obtener

function obtenerUsuarios() {
    var datos = localStorage.getItem("usuarios");
    if (datos) {
        return JSON.parse(datos);
    }
    return [];
}

function guardarUsuario(nombre, email, password) {
    var usuarios = obtenerUsuarios();
    usuarios.push({ nombre: nombre, email: email, password: password });
    localStorage.setItem("usuarios", JSON.stringify(usuarios));
}

function existeEmail(email) {
    var usuarios = obtenerUsuarios();
    for (var i = 0; i < usuarios.length; i++) {
        if (usuarios[i].email === email) {
            return true;
        }
    }
    return false;
}

function verificarCredenciales(email, password) {
    var usuarios = obtenerUsuarios();
    for (var i = 0; i < usuarios.length; i++) {
        if (usuarios[i].email === email && usuarios[i].password === password) {
            return usuarios[i];
        }
    }
    return null;
}

// SESIÓN: guardar y verificar

function guardarSesion(nombre, email) {
    localStorage.setItem("sesion_activa", "true");
    localStorage.setItem("sesion_nombre", nombre);
    localStorage.setItem("sesion_email", email);
}

function haySesion() {
    return localStorage.getItem("sesion_activa") === "true";
}

function cerrarSesion() {
    localStorage.removeItem("sesion_activa");
    localStorage.removeItem("sesion_nombre");
    localStorage.removeItem("sesion_email");
    window.location.href = "../login/index.html";
}

// Función global para cerrar sesión
window.cerrarSesionGlobal = cerrarSesion;