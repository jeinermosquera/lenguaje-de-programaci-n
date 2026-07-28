document.addEventListener('DOMContentLoaded', function () {
    AOS.init({ duration: 600, once: true });
    initPasswordToggles();
    initAuthToggle();

    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);

    if (window.location.hash === '#register') {
        setTimeout(showRegister, 200);
    }
});

/* ─── Toggle between login / register ─── */
function showLogin() {
    document.getElementById('loginPanel').style.display = '';
    document.getElementById('registerPanel').style.display = 'none';
    document.getElementById('authCardTitle').textContent = 'Iniciar sesi\u00f3n';
    document.getElementById('authCardSubtitle').textContent = 'Ingresa tus credenciales para continuar';
}

function showRegister() {
    document.getElementById('loginPanel').style.display = 'none';
    document.getElementById('registerPanel').style.display = '';
    document.getElementById('authCardTitle').textContent = 'Crear cuenta';
    document.getElementById('authCardSubtitle').textContent = '\u00danete a la comunidad y mantente informado';
}

function initAuthToggle() {
    var showReg = document.getElementById('showRegister');
    var showLog = document.getElementById('showLogin');
    if (showReg) showReg.addEventListener('click', function (e) { e.preventDefault(); showRegister(); });
    if (showLog) showLog.addEventListener('click', function (e) { e.preventDefault(); showLogin(); });
}

/* ─── Toggle password visibility ─── */
function initPasswordToggles() {
    function toggle(btnId, inputId) {
        var btn = document.getElementById(btnId);
        var input = document.getElementById(inputId);
        if (!btn || !input) return;
        btn.addEventListener('click', function () {
            var type = input.type === 'password' ? 'text' : 'password';
            input.type = type;
            this.querySelector('i').className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
        });
    }
    toggle('toggleLoginPass', 'loginContrasena');
    toggle('toggleRegPass', 'regContrasena');
}

/* ─── Toast helper (SweetAlert2) ─── */
function showToast(message, type) {
    var config = {
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: function (t) {
            t.addEventListener('mouseenter', Swal.stopTimer);
            t.addEventListener('mouseleave', Swal.resumeTimer);
        }
    };

    switch (type) {
        case 'success':
            config.icon = 'success';
            config.title = message;
            config.background = '#d1e7dd';
            config.color = '#0f5132';
            break;
        case 'error':
            config.icon = 'error';
            config.title = message;
            config.background = '#f8d7da';
            config.color = '#842029';
            break;
        default:
            config.title = message;
    }

    Swal.fire(config);
}

/* ─── Loading state ─── */
function setLoading(btnId, spinnerId, textId, loading) {
    document.getElementById(btnId).disabled = loading;
    document.getElementById(spinnerId).classList.toggle('d-none', !loading);
    document.getElementById(textId).classList.toggle('d-none', loading);
}

/* ─── Login ─── */
async function handleLogin(e) {
    e.preventDefault();

    var correo = document.getElementById('loginCorreo').value.trim();
    var contrasena = document.getElementById('loginContrasena').value;

    if (!correo || !contrasena) {
        showToast('Completa todos los campos.', 'error');
        return;
    }

    setLoading('btnLogin', 'loginSpinner', 'loginText', true);

    try {
        var res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correo: correo, contrasena: contrasena })
        });
        var data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
            var destino = data.rol === 'admin' ? '/admin/' : '/user/';
            setTimeout(function () { window.location.href = destino; }, 1000);
        } else {
            showToast(data.message, 'error');
            setLoading('btnLogin', 'loginSpinner', 'loginText', false);
        }
    } catch (e) {
        showToast('Error de conexi\u00f3n. Intenta de nuevo.', 'error');
        setLoading('btnLogin', 'loginSpinner', 'loginText', false);
    }
}

/* ─── Register ─── */
async function handleRegister(e) {
    e.preventDefault();

    var nombreCompleto = document.getElementById('regNombreCompleto').value.trim();
    var correo = document.getElementById('regCorreo').value.trim();
    var contrasena = document.getElementById('regContrasena').value;
    var confirmar = document.getElementById('regConfirmar').value;

    if (!nombreCompleto || !correo || !contrasena || !confirmar) {
        showToast('Completa todos los campos.', 'error');
        return;
    }

    if (contrasena.length < 6) {
        showToast('La contrase\u00f1a debe tener al menos 6 caracteres.', 'error');
        return;
    }

    if (contrasena !== confirmar) {
        showToast('Las contrase\u00f1as no coinciden.', 'error');
        return;
    }

    var partes = nombreCompleto.split(' ');
    var nombre = partes[0];
    var apellido = partes.slice(1).join(' ') || '';

    if (!nombre) {
        showToast('Ingresa un nombre v\u00e1lido.', 'error');
        return;
    }

    setLoading('btnRegister', 'registerSpinner', 'registerText', true);

    try {
        var payload = { nombre: nombre, apellido: apellido, correo: correo, contrasena: contrasena };

        var res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        var data = await res.json();

        if (data.success) {
            showToast(data.message, 'success');
            document.getElementById('registerForm').reset();
            showLogin();
        } else {
            showToast(data.message, 'error');
        }
    } catch (e) {
        showToast('Error de conexi\u00f3n. Intenta de nuevo.', 'error');
    }

    setLoading('btnRegister', 'registerSpinner', 'registerText', false);
}