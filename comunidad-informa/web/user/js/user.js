var CATEGORIAS_NOTICIAS = ['General', 'Deportes', 'Cultura', 'Educacion', 'Salud', 'Tecnologia', 'Politica'];
var CATEGORIAS_EVENTOS = ['General', 'Reunion', 'Taller', 'Cultural', 'Deportivo', 'Social', 'Capacitacion'];
var categoriaActual = null;

document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('filtroCategorias')) {
        var esEventos = !!document.getElementById('eventosList');
        var cats = esEventos ? CATEGORIAS_EVENTOS : CATEGORIAS_NOTICIAS;
        renderFiltroCategorias(cats);
    }
    var btnFecha = document.getElementById('btnFiltrarFecha');
    if (btnFecha) {
        btnFecha.addEventListener('click', function () { recargar(); });
    }
    if (document.getElementById('publicacionesList')) {
        cargarPublicaciones();
    }
    if (document.getElementById('eventosList')) {
        cargarEventos();
    }
    if (document.getElementById('comentariosList')) {
        cargarComentarios();
    }
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
    var esEventos = !!document.getElementById('eventosList');
    if (esEventos) {
        cargarEventos();
    } else {
        cargarPublicaciones();
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
    if (anio && anio.value) params.push('anio=' + encodeURIComponent(anio.value));
    if (mes && mes.value) params.push('mes=' + encodeURIComponent(mes.value));
    if (dia && dia.value) params.push('dia=' + encodeURIComponent(dia.value));
    return params.length ? '?' + params.join('&') : '';
}

/* ─── Home: Lista de publicaciones ─── */
async function cargarPublicaciones() {
    var container = document.getElementById('publicacionesList');
    try {
        var res = await fetch('/api/user/publicaciones' + urlParams());
        var data = await res.json();
        container.innerHTML = '';
        if (!data.success || data.data.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-light text-center">No hay publicaciones.</div></div>';
            return;
        }
        for (var i = 0; i < data.data.length; i++) {
            var p = data.data[i];
            var col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4 d-flex';
            col.innerHTML = '\
                <div class="news-card flex-grow-1" onclick="window.location.href=\'/user/publicacion/' + p.id + '\'">\
                    ' + (p.imagen
                        ? '<img src="' + escapeHtml(p.imagen) + '" alt="' + escapeHtml(p.titulo) + '" class="card-img-top" loading="lazy">'
                        : '<div class="img-placeholder"><i class="bi bi-newspaper"></i></div>'
                    ) + '\
                    <div class="card-body d-flex flex-column">\
                        <div class="d-flex gap-2 align-items-center mb-2">\
                            <span class="badge rounded-pill" style="background:rgba(57,88,109,0.1);color:var(--accent);font-size:0.65rem;">' + escapeHtml(p.categoria || 'General') + '</span>\
                        </div>\
                        <h5 class="news-title mb-2">' + escapeHtml(p.titulo) + '</h5>\
                        <p class="news-summary mb-3 flex-grow-1">' + escapeHtml(p.contenido.substring(0, 120)) + (p.contenido.length > 120 ? '...' : '') + '</p>\
                        <div class="news-meta">\
                            <i class="bi bi-person-circle"></i>\
                            <span>' + escapeHtml(p.nombre) + ' ' + escapeHtml(p.apellido) + '</span>\
                            <i class="bi bi-dot"></i>\
                            <span>' + formatDate(p.fecha_publicacion) + '</span>\
                        </div>\
                    </div>\
                </div>';
            container.appendChild(col);
        }
    } catch (e) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-danger text-center">Error al cargar.</div></div>';
    }
}

/* ─── Detalle: Comentarios ─── */
async function cargarComentarios() {
    var container = document.getElementById('comentariosList');
    try {
        var res = await fetch('/api/user/publicaciones/' + PUB_ID);
        var data = await res.json();
        container.innerHTML = '';
        if (!data.success || !data.data.comentarios || data.data.comentarios.length === 0) {
            container.innerHTML = '<p class="text-muted small mb-0">No hay comentarios aún.</p>';
            return;
        }
        for (var i = 0; i < data.data.comentarios.length; i++) {
            var c = data.data.comentarios[i];
            var item = document.createElement('div');
            item.className = 'comment-item';
            item.innerHTML = '\
                <div class="d-flex gap-2 mb-1">\
                    <div class="fw-semibold small" style="color:var(--primary);">' + escapeHtml(c.nombre) + ' ' + escapeHtml(c.apellido) + '</div>\
                    <span class="comment-meta">· ' + formatDate(c.fecha_comentario) + '</span>\
                </div>\
                <div class="comment-body">' + escapeHtml(c.contenido) + '</div>';
            container.appendChild(item);
        }
    } catch (e) {
        container.innerHTML = '<p class="text-danger small">Error al cargar comentarios.</p>';
    }
}

/* ─── Eventos ─── */
async function cargarEventos() {
    var container = document.getElementById('eventosList');
    try {
        var res = await fetch('/api/user/eventos' + urlParams());
        var data = await res.json();
        container.innerHTML = '';
        if (!data.success || data.data.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-light text-center">No hay eventos próximos.</div></div>';
            return;
        }
        for (var i = 0; i < data.data.length; i++) {
            var e = data.data[i];
            var col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4 d-flex';
            col.innerHTML = '\
                <div class="event-card flex-grow-1" onclick="window.location.href=\'/user/evento/' + e.id + '\'">\
                    ' + (e.imagen
                        ? '<img src="' + escapeHtml(e.imagen) + '" alt="' + escapeHtml(e.titulo) + '" class="event-card-img" loading="lazy">'
                        : '<div class="event-img-placeholder"><i class="bi bi-calendar-event"></i></div>'
                    ) + '\
                    <div class="event-date-badge">\
                        <span class="event-day">' + formatDay(e.fecha_evento) + '</span>\
                        <span class="event-month">' + formatMonth(e.fecha_evento) + '</span>\
                    </div>\
                    <div class="card-body d-flex flex-column">\
                        <h5 class="event-title">' + escapeHtml(e.titulo) + '</h5>\
                        <p class="event-desc flex-grow-1">' + escapeHtml(e.descripcion) + '</p>\
                        <div class="event-meta">\
                            <i class="bi bi-geo-alt"></i>\
                            <span>' + escapeHtml(e.ubicacion || 'Por definir') + '</span>\
                            <i class="bi bi-dot"></i>\
                            <span>' + escapeHtml(e.nombre || '') + ' ' + escapeHtml(e.apellido || '') + '</span>\
                        </div>\
                    </div>\
                </div>';
            container.appendChild(col);
        }
    } catch (e) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-danger text-center">Error al cargar eventos.</div></div>';
    }
}

function formatDay(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).getDate();
}

function formatMonth(dateStr) {
    if (!dateStr) return '';
    var meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return meses[new Date(dateStr).getMonth()];
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
