var CATEGORIAS_NOTICIAS = ['General', 'Deportes', 'Cultura', 'Educacion', 'Salud', 'Tecnologia', 'Politica'];
var CATEGORIAS_EVENTOS = ['General', 'Reunion', 'Taller', 'Cultural', 'Deportivo', 'Social', 'Capacitacion'];
var categoriaActual = null;

document.addEventListener('DOMContentLoaded', function () {
    var catContainer = document.getElementById('filtroCategorias');
    if (catContainer) {
        var esEventos = !!document.getElementById('eventosTableBody');
        renderFiltroCategorias(esEventos ? CATEGORIAS_EVENTOS : CATEGORIAS_NOTICIAS);
    }
    var btnFecha = document.getElementById('btnFiltrarFecha');
    if (btnFecha) {
        btnFecha.addEventListener('click', function () { recargar(); });
    }
    if (document.getElementById('statsContainer')) cargarDashboard();
    if (document.getElementById('noticiasTableBody')) cargarNoticias();
    if (document.getElementById('eventosTableBody')) cargarEventos();
    if (document.getElementById('usuariosTableBody')) cargarUsuarios();
    if (document.getElementById('noticiaForm')) initNoticiaForm();
    if (document.getElementById('eventoForm')) initEventoForm();

    var btnLogout = document.getElementById('btnLogout');
    if (btnLogout) {
        btnLogout.addEventListener('click', function (e) {
            e.preventDefault();
            fetch('/api/logout', { method: 'POST' }).then(function () {
                window.location.href = '/';
            });
        });
    }
});

function renderFiltroCategorias(categorias) {
    var container = document.getElementById('filtroCategorias');
    var todas = document.createElement('button');
    todas.className = 'cat-pill' + (!categoriaActual ? ' active' : '');
    todas.textContent = 'Todas';
    todas.addEventListener('click', function () {
        if (categoriaActual !== null) {
            categoriaActual = null;
            recargar();
        }
    });
    container.appendChild(todas);
    for (var i = 0; i < categorias.length; i++) {
        var btn = document.createElement('button');
        btn.className = 'cat-pill' + (categoriaActual === categorias[i] ? ' active' : '');
        btn.textContent = categorias[i];
        btn.addEventListener('click', (function (cat) {
            return function () {
                if (categoriaActual !== cat) {
                    categoriaActual = cat;
                    recargar();
                }
            };
        })(categorias[i]));
        container.appendChild(btn);
    }
}

function recargar() {
    var esEventos = !!document.getElementById('eventosTableBody');
    if (esEventos) {
        cargarEventos();
    } else {
        cargarNoticias();
    }
    var pills = document.querySelectorAll('.cat-pill');
    for (var i = 0; i < pills.length; i++) {
        pills[i].classList.toggle('active', pills[i].textContent === (categoriaActual || 'Todas'));
    }
}

function urlParams() {
    var params = [];
    if (categoriaActual) params.push('categoria=' + encodeURIComponent(categoriaActual));
    var anio = document.getElementById('filtroAnio');
    var mes = document.getElementById('filtroMes');
    var dia = document.getElementById('filtroDia');
    if (anio && anio.value) params.push('anio=' + anio.value);
    if (mes && mes.value) params.push('mes=' + mes.value);
    if (dia && dia.value) params.push('dia=' + dia.value);
    return params.length ? '?' + params.join('&') : '';
}

/* ─── Dashboard ─── */
async function cargarDashboard() {
    try {
        var [pub, ev, usr] = await Promise.all([
            fetch('/api/admin/publicaciones').then(function (r) { return r.json(); }),
            fetch('/api/admin/eventos').then(function (r) { return r.json(); }),
            fetch('/api/admin/usuarios').then(function (r) { return r.json(); })
        ]);
        document.getElementById('statNoticias').textContent = pub.data ? pub.data.length : 0;
        document.getElementById('statEventos').textContent = ev.data ? ev.data.length : 0;
        document.getElementById('statUsuarios').textContent = usr.data ? usr.data.length : 0;

        renderUltimas(pub.data, 'ultimasNoticias', '/admin/noticias/', 'noticias');
        renderUltimas(ev.data, 'ultimosEventos', '/admin/eventos/', 'eventos');
    } catch (e) {
        document.getElementById('ultimasNoticias').innerHTML = '<p class="text-danger small mb-0">Error al cargar.</p>';
        document.getElementById('ultimosEventos').innerHTML = '<p class="text-danger small mb-0">Error al cargar.</p>';
    }
}

function renderUltimas(data, containerId, linkPrefix, type) {
    var container = document.getElementById(containerId);
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="text-muted small mb-0">No hay ' + type + '.</p>';
        return;
    }
    var html = '';
    var max = Math.min(data.length, 5);
    for (var i = 0; i < max; i++) {
        var item = data[i];
        var titulo = item.titulo || '(sin titulo)';
        var fecha = item.fecha_publicacion || item.fecha_evento;
        var categoria = item.categoria || 'General';
        if (type === 'eventos') {
            html += '<div class="d-flex justify-content-between align-items-center py-2 border-bottom" style="border-color:var(--border)!important;">' +
                '<div><span class="fw-semibold small">' + escapeHtml(titulo) + '</span><br><span class="text-muted" style="font-size:0.75rem;">' + escapeHtml(categoria) + ' · ' + formatDate(fecha) + '</span></div>' +
                '<a href="' + linkPrefix + item.id + '" class="btn btn-sm btn-outline-accent rounded-pill px-2" style="font-size:0.75rem;">Ver</a></div>';
        } else {
            html += '<div class="d-flex justify-content-between align-items-center py-2 border-bottom" style="border-color:var(--border)!important;">' +
                '<div><span class="fw-semibold small">' + escapeHtml(titulo) + '</span><br><span class="text-muted" style="font-size:0.75rem;">' + escapeHtml(categoria) + ' · ' + formatDate(fecha) + '</span></div>' +
                '<a href="' + linkPrefix + item.id + '/editar" class="btn btn-sm btn-outline-accent rounded-pill px-2" style="font-size:0.75rem;">Editar</a></div>';
        }
    }
    container.innerHTML = html;
}

/* ─── Noticias CRUD ─── */
async function cargarNoticias() {
    var tbody = document.getElementById('noticiasTableBody');
    var empty = document.getElementById('noticiasEmpty');
    try {
        var res = await fetch('/api/admin/publicaciones' + urlParams());
        var data = await res.json();
        tbody.innerHTML = '';
        if (!data.success || data.data.length === 0) {
            tbody.classList.add('d-none');
            empty.classList.remove('d-none');
            return;
        }
        tbody.classList.remove('d-none');
        empty.classList.add('d-none');
        for (var i = 0; i < data.data.length; i++) {
            var p = data.data[i];
            var tr = document.createElement('tr');
            tr.innerHTML = '<td><span class="fw-semibold">' + escapeHtml(p.titulo) + '</span></td>' +
                '<td><span class="badge rounded-pill" style="background:rgba(57,88,109,0.1);color:var(--accent);font-size:0.75rem;">' + escapeHtml(p.categoria || 'General') + '</span></td>' +
                '<td class="text-secondary">' + escapeHtml(p.nombre) + ' ' + escapeHtml(p.apellido) + '</td>' +
                '<td class="text-secondary" style="font-size:0.82rem;">' + formatDate(p.fecha_publicacion) + '</td>' +
                '<td class="text-end">' +
                    '<a href="/admin/noticias/' + p.id + '/editar" class="btn btn-sm btn-outline-accent rounded-pill px-2 me-1" style="font-size:0.75rem;"><i class="bi bi-pencil"></i></a>' +
                    '<button class="btn btn-sm btn-outline-danger rounded-pill px-2" style="font-size:0.75rem;" onclick="eliminarNoticia(' + p.id + ')"><i class="bi bi-trash"></i></button>' +
                '</td>';
            tbody.appendChild(tr);
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger small">Error al cargar.</td></tr>';
    }
}

function eliminarNoticia(id) {
    Swal.fire({
        title: 'Eliminar noticia?',
        text: 'Esta accion no se puede deshacer.',
        icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#6c757d',
        confirmButtonText: 'Eliminar', cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) {
            fetch('/api/admin/publicaciones/' + id, { method: 'DELETE' }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.success) {
                    Swal.fire('Eliminado', d.message, 'success');
                    cargarNoticias();
                } else {
                    Swal.fire('Error', d.message, 'error');
                }
            });
        }
    });
}

function initImagePreview(inputId, previewId) {
    var input = document.getElementById(inputId);
    var preview = document.getElementById(previewId);
    if (!input || !preview) return;
    input.addEventListener('change', function () {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function (e) {
                preview.querySelector('img').src = e.target.result;
                preview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    });
}

function uploadImage(input) {
    return new Promise(function (resolve, reject) {
        var file = input.files[0];
        if (!file) return resolve(null);
        var formData = new FormData();
        formData.append('imagen', file);
        fetch('/api/upload', { method: 'POST', body: formData })
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (d.success) resolve(d.url);
                else reject(d.message);
            })
            .catch(reject);
    });
}

function initNoticiaForm() {
    initImagePreview('imagenInput', 'imagenPreview');
    document.getElementById('noticiaForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var id = document.getElementById('noticiaId').value;
        var btn = this.querySelector('button[type="submit"]');
        btn.disabled = true;

        uploadImage(document.getElementById('imagenInput')).then(function (imgUrl) {
            var data = {
                titulo: document.getElementById('titulo').value.trim(),
                contenido: document.getElementById('contenido').value.trim(),
                categoria: document.getElementById('categoria').value,
                imagen: imgUrl || document.getElementById('imagen').value.trim() || null
            };
            if (!data.titulo || !data.contenido) {
                Swal.fire('Error', 'Titulo y contenido son obligatorios.', 'error');
                btn.disabled = false;
                return;
            }
            var url = '/api/admin/publicaciones' + (id ? '/' + id : '');
            var method = id ? 'PUT' : 'POST';

            fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    if (d.success) {
                        Swal.fire({ icon: 'success', title: d.message, timer: 1500, showConfirmButton: false }).then(function () {
                            window.location.href = '/admin/noticias';
                        });
                    } else {
                        Swal.fire('Error', d.message, 'error');
                        btn.disabled = false;
                    }
                }).catch(function () {
                    Swal.fire('Error', 'Error al guardar.', 'error');
                    btn.disabled = false;
                });
        }).catch(function (msg) {
            Swal.fire('Error', msg || 'Error al subir imagen.', 'error');
            btn.disabled = false;
        });
    });
}

/* ─── Eventos CRUD ─── */
async function cargarEventos() {
    var tbody = document.getElementById('eventosTableBody');
    var empty = document.getElementById('eventosEmpty');
    if (!tbody) return;
    try {
        var res = await fetch('/api/admin/eventos' + urlParams());
        var data = await res.json();
        tbody.innerHTML = '';
        if (!data.success || data.data.length === 0) {
            tbody.classList.add('d-none');
            empty.classList.remove('d-none');
            return;
        }
        tbody.classList.remove('d-none');
        empty.classList.add('d-none');
        for (var i = 0; i < data.data.length; i++) {
            var e = data.data[i];
            var tr = document.createElement('tr');
            tr.innerHTML = '<td><span class="fw-semibold">' + escapeHtml(e.titulo) + '</span></td>' +
                '<td class="text-secondary" style="font-size:0.82rem;">' + formatDate(e.fecha_evento) + '</td>' +
                '<td class="text-secondary">' + escapeHtml(e.ubicacion || '') + '</td>' +
                '<td><span class="badge rounded-pill" style="background:rgba(57,88,109,0.1);color:var(--accent);font-size:0.75rem;">' + escapeHtml(e.categoria || 'General') + '</span></td>' +
                '<td class="text-end">' +
                    '<a href="/admin/eventos/' + e.id + '/editar" class="btn btn-sm btn-outline-accent rounded-pill px-2 me-1" style="font-size:0.75rem;"><i class="bi bi-pencil"></i></a>' +
                    '<button class="btn btn-sm btn-outline-danger rounded-pill px-2" style="font-size:0.75rem;" onclick="eliminarEvento(' + e.id + ')"><i class="bi bi-trash"></i></button>' +
                '</td>';
            tbody.appendChild(tr);
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger small">Error al cargar.</td></tr>';
    }
}

function eliminarEvento(id) {
    Swal.fire({
        title: 'Eliminar evento?',
        text: 'Esta accion no se puede deshacer.',
        icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#6c757d',
        confirmButtonText: 'Eliminar', cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) {
            fetch('/api/admin/eventos/' + id, { method: 'DELETE' }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.success) {
                    Swal.fire('Eliminado', d.message, 'success');
                    cargarEventos();
                } else {
                    Swal.fire('Error', d.message, 'error');
                }
            });
        }
    });
}

function initEventoForm() {
    initImagePreview('imagenInput', 'imagenPreview');
    var form = document.getElementById('eventoForm');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        var id = document.getElementById('eventoId').value;
        var btn = this.querySelector('button[type="submit"]');
        btn.disabled = true;

        uploadImage(document.getElementById('imagenInput')).then(function (imgUrl) {
            var data = {
                titulo: document.getElementById('titulo').value.trim(),
                descripcion: document.getElementById('descripcion').value.trim(),
                fecha_evento: document.getElementById('fecha_evento').value,
                ubicacion: document.getElementById('ubicacion').value.trim(),
                categoria: document.getElementById('categoria').value,
                imagen: imgUrl || document.getElementById('imagen').value.trim() || null
            };
            if (!data.titulo || !data.fecha_evento) {
                Swal.fire('Error', 'Titulo y fecha del evento son obligatorios.', 'error');
                btn.disabled = false;
                return;
            }
            var url = '/api/admin/eventos' + (id ? '/' + id : '');
            var method = id ? 'PUT' : 'POST';

            fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    if (d.success) {
                        Swal.fire({ icon: 'success', title: d.message, timer: 1500, showConfirmButton: false }).then(function () {
                            window.location.href = '/admin/eventos';
                        });
                    } else {
                        Swal.fire('Error', d.message, 'error');
                        btn.disabled = false;
                    }
                }).catch(function () {
                    Swal.fire('Error', 'Error al guardar.', 'error');
                    btn.disabled = false;
                });
        }).catch(function (msg) {
            Swal.fire('Error', msg || 'Error al subir imagen.', 'error');
            btn.disabled = false;
        });
    });
}

/* ─── Usuarios ─── */
async function cargarUsuarios() {
    var tbody = document.getElementById('usuariosTableBody');
    var empty = document.getElementById('usuariosEmpty');
    try {
        var res = await fetch('/api/admin/usuarios');
        var data = await res.json();
        tbody.innerHTML = '';
        if (!data.success || data.data.length === 0) {
            tbody.classList.add('d-none');
            empty.classList.remove('d-none');
            return;
        }
        tbody.classList.remove('d-none');
        empty.classList.add('d-none');
        for (var i = 0; i < data.data.length; i++) {
            var u = data.data[i];
            var tr = document.createElement('tr');
            tr.innerHTML = '<td><span class="fw-semibold">' + escapeHtml(u.nombre) + ' ' + escapeHtml(u.apellido) + '</span></td>' +
                '<td class="text-secondary">' + escapeHtml(u.correo) + '</td>' +
                '<td>' +
                    '<select class="form-select form-select-sm d-inline-block" style="width:auto;" onchange="cambiarRol(' + u.id + ', this.value)">' +
                        '<option value="usuario"' + (u.rol === 'usuario' ? ' selected' : '') + '>Usuario</option>' +
                        '<option value="admin"' + (u.rol === 'admin' ? ' selected' : '') + '>Admin</option>' +
                    '</select>' +
                '</td>' +
                '<td class="text-secondary" style="font-size:0.82rem;">' + (u.fecha_registro ? formatDate(u.fecha_registro) : '') + '</td>' +
                '<td class="text-end">' +
                    '<button class="btn btn-sm btn-outline-danger rounded-pill px-2" style="font-size:0.75rem;" onclick="eliminarUsuario(' + u.id + ')"><i class="bi bi-trash"></i></button>' +
                '</td>';
            tbody.appendChild(tr);
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger small">Error al cargar.</td></tr>';
    }
}

function cambiarRol(id, rol) {
    fetch('/api/admin/usuarios/' + id + '/rol', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rol: rol })
    }).then(function (r) { return r.json(); }).then(function (d) {
        if (d.success) {
            Swal.fire({ icon: 'success', title: 'Rol actualizado', timer: 1200, showConfirmButton: false });
        } else {
            Swal.fire('Error', d.message, 'error');
        }
    });
}

function eliminarUsuario(id) {
    Swal.fire({
        title: 'Eliminar usuario?', text: 'Esta accion no se puede deshacer.', icon: 'warning',
        showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#6c757d',
        confirmButtonText: 'Eliminar', cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) {
            fetch('/api/admin/usuarios/' + id, { method: 'DELETE' }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.success) {
                    Swal.fire('Eliminado', d.message, 'success');
                    cargarUsuarios();
                } else {
                    Swal.fire('Error', d.message, 'error');
                }
            });
        }
    });
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    var d = new Date(dateStr);
    var meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return d.getDate() + ' ' + meses[d.getMonth()] + ' ' + d.getFullYear();
}

function escapeHtml(text) {
    if (!text) return '';
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}
