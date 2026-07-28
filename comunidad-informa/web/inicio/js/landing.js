document.addEventListener('DOMContentLoaded', function () {
    AOS.init({ duration: 600, easing: 'ease-out-cubic', once: true, offset: 50 });
    initNavbarScroll();
    loadPublicas();
    loadEventos();
    initSmoothScroll();
});

/* ─── Navbar scroll effect ─── */
function initNavbarScroll() {
    var navbar = document.querySelector('.landing-navbar');
    if (!navbar) return;
    window.addEventListener('scroll', function () {
        navbar.classList.toggle('navbar-scrolled', window.scrollY > 80);
    });
}

/* ─── Smooth scroll ─── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/* ─── Load Publicaciones ─── */
async function loadPublicas() {
    try {
        var res = await fetch('/api/publicas');
        var data = await res.json();
        if (!data.success) return;

        updateStats(data.data.length);

        if (data.data.length === 0) {
            document.getElementById('publicacionesList').innerHTML = '<div class="col-12"><div class="alert alert-light text-center">No hay publicaciones aún.</div></div>';
            return;
        }

        renderNewsCards(data.data);
    } catch (e) {
        document.getElementById('publicacionesList').innerHTML = '<div class="col-12"><div class="alert alert-danger text-center">Error al cargar noticias.</div></div>';
    }
    AOS.refresh();
}

function renderFeatured(post) {
    var container = document.getElementById('featuredPost');
    if (!container) return;

    var fecha = new Date(post.fecha_publicacion);
    var readingTime = Math.max(1, Math.ceil(post.contenido.length / 500));

    container.innerHTML = '\
        <div class="featured-card cursor-pointer" onclick="window.location.href=\'/login\'" role="button">\
            <div class="position-relative">\
                <span class="featured-badge badge bg-danger rounded-pill px-3 py-1">Destacado</span>\
                ' + (post.imagen
                    ? '<img src="' + escapeHtml(post.imagen) + '" alt="' + escapeHtml(post.titulo) + '" class="featured-image" loading="lazy">'
                    : '<div class="featured-image-placeholder"><i class="bi bi-newspaper"></i></div>'
                ) + '\
            </div>\
            <div class="featured-content">\
                <div class="d-flex gap-2 align-items-center mb-2">\
                    <span class="badge rounded-pill" style="background:rgba(57,88,109,0.1);color:#39586D;">Noticia</span>\
                    <span class="small text-muted"><i class="bi bi-clock me-1"></i>' + readingTime + ' min lectura</span>\
                </div>\
                <h3 class="featured-title mb-2"><a href="/login">' + escapeHtml(post.titulo) + '</a></h3>\
                <p class="text-muted small mb-3">' + escapeHtml(post.contenido.substring(0, 200)) + (post.contenido.length > 200 ? '...' : '') + '</p>\
                <div class="news-meta">\
                    ' + getAuthorAvatar(post) + '\
                    <span class="fw-semibold text-dark">' + escapeHtml(post.nombre) + ' ' + escapeHtml(post.apellido) + '</span>\
                    <i class="bi bi-dot"></i>\
                    <span>' + formatDate(fecha) + '</span>\
                </div>\
            </div>\
        </div>';
}

function renderNewsCards(posts) {
    var container = document.getElementById('publicacionesList');
    container.innerHTML = '';

    if (posts.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-muted text-center small">No hay más noticias.</p></div>';
        return;
    }

    for (var i = 0; i < posts.length; i++) {
        var p = posts[i];
        var col = document.createElement('div');
        col.className = 'col-md-6 d-flex';
        col.setAttribute('data-aos', 'fade-up');
        col.setAttribute('data-aos-delay', String((i % 3) * 100));

        var fecha = new Date(p.fecha_publicacion);
        var readingTime = Math.max(1, Math.ceil(p.contenido.length / 500));

        col.innerHTML = '\
            <div class="news-card cursor-pointer flex-grow-1" onclick="window.location.href=\'/login\'" role="button">\
                ' + (p.imagen
                    ? '<img src="' + escapeHtml(p.imagen) + '" alt="' + escapeHtml(p.titulo) + '" class="card-img-top" loading="lazy">'
                    : '<div class="img-placeholder"><i class="bi bi-image"></i></div>'
                ) + '\
                <div class="card-body d-flex flex-column">\
                    <div class="d-flex gap-2 align-items-center mb-2">\
                        <span class="badge rounded-pill" style="background:rgba(57,88,109,0.1);color:#39586D;font-size:0.65rem;">Noticia</span>\
                        <span class="small text-muted" style="font-size:0.7rem;"><i class="bi bi-clock me-1"></i>' + readingTime + ' min</span>\
                    </div>\
                    <h5 class="news-title mb-2"><a href="/login">' + escapeHtml(p.titulo) + '</a></h5>\
                    <p class="news-summary mb-3 flex-grow-1">' + escapeHtml(p.contenido.substring(0, 120)) + (p.contenido.length > 120 ? '...' : '') + '</p>\
                    <div class="d-flex justify-content-between align-items-center">\
                        <div class="news-meta">\
                            ' + getAuthorAvatar(p) + '\
                            <span>' + formatDate(fecha) + '</span>\
                        </div>\
                        <span class="btn btn-sm btn-outline-primary rounded-pill" style="font-size:0.75rem;">Leer <i class="bi bi-arrow-right ms-1"></i></span>\
                    </div>\
                </div>\
            </div>';
        container.appendChild(col);
    }
}

/* ─── Load Eventos ─── */
async function loadEventos() {
    var container = document.getElementById('eventosList');
    try {
        var res = await fetch('/api/publicas/eventos');
        var data = await res.json();
        container.innerHTML = '';

        if (!data.success || data.data.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-light text-center">No hay eventos próximos.</div></div>';
            updateStats(0, true);
            return;
        }

        updateStats(data.data.length, true);

        var max = Math.min(data.data.length, 3);
        for (var i = 0; i < max; i++) {
            var ev = data.data[i];
            var col = document.createElement('div');
            col.className = 'col-md-4 d-flex';
            col.setAttribute('data-aos', 'fade-up');
            col.setAttribute('data-aos-delay', String(i * 100));

            var fecha = new Date(ev.fecha_evento);
            var meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            var diasSem = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

            col.innerHTML = '\
                <div class="event-card cursor-pointer flex-grow-1" onclick="window.location.href=\'/login\'" role="button">\
                    ' + (ev.imagen
                        ? '<img src="' + escapeHtml(ev.imagen) + '" alt="' + escapeHtml(ev.titulo) + '" class="event-card-img" loading="lazy">'
                        : ''
                    ) + '\
                    <div class="card-body">\
                        <div class="d-flex gap-3">\
                            <div class="event-date-block">\
                                <div class="day">' + fecha.getDate() + '</div>\
                                <div class="month">' + meses[fecha.getMonth()] + '</div>\
                            </div>\
                            <div class="flex-grow-1 min-w-0">\
                                <div class="event-title mb-1">' + escapeHtml(ev.titulo) + '</div>\
                                <div class="event-location mb-1"><i class="bi bi-calendar me-1"></i>' + diasSem[fecha.getDay()] + ' ' + fecha.getDate() + ' de ' + meses[fecha.getMonth()] + '</div>\
                                ' + (ev.ubicacion ? '<div class="event-location mb-1"><i class="bi bi-geo-alt me-1"></i>' + escapeHtml(ev.ubicacion) + '</div>' : '') + '\
                                ' + (ev.descripcion ? '<div class="event-desc">' + escapeHtml(ev.descripcion.substring(0, 80)) + '</div>' : '') + '\
                            </div>\
                        </div>\
                        <div class="text-end mt-3">\
                            <span class="btn btn-sm btn-outline-success rounded-pill" style="font-size:0.75rem;">Ver detalles <i class="bi bi-arrow-right ms-1"></i></span>\
                        </div>\
                    </div>\
                </div>';
            container.appendChild(col);
        }
    } catch (e) {
        container.innerHTML = '<div class="col-12"><div class="alert alert-danger text-center">Error al cargar eventos.</div></div>';
    }
    AOS.refresh();
}

/* ─── Helpers ─── */
function getAuthorAvatar(post) {
    if (post.fotografia) {
        return '<img src="' + escapeHtml(post.fotografia) + '" alt="Avatar" class="author-avatar" loading="lazy">';
    }
    var initials = (post.nombre ? post.nombre.charAt(0).toUpperCase() : '') + (post.apellido ? post.apellido.charAt(0).toUpperCase() : '');
    return '<div class="author-avatar-placeholder"><span class="fw-semibold" style="font-size:0.6rem;">' + initials + '</span></div>';
}

function formatDate(date) {
    var options = { month: 'short', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('es-ES', options);
}

function updateStats(count, isEvent) {
    if (isEvent) {
        var el = document.getElementById('totalEventos');
        if (el) el.textContent = count;
    } else {
        var el = document.getElementById('totalNoticias');
        if (el) el.textContent = count;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}