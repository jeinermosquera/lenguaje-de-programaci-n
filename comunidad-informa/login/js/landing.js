document.addEventListener('DOMContentLoaded', function () {
    AOS.init({ duration: 600, easing: 'ease-out-cubic', once: true, offset: 50 });
    initCanvas();
    initNavbarScroll();
    loadPublicas();
    loadEventos();
    initSearch();
    initNewsletter();
    initSmoothScroll();
});

/* ─── Canvas: Particle Network ─── */
function initCanvas() {
    var canvas = document.getElementById('heroCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var particles = [];
    var mouse = { x: null, y: null };
    var W, H;

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    canvas.addEventListener('mousemove', function (e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    canvas.addEventListener('mouseleave', function () {
        mouse.x = null;
        mouse.y = null;
    });

    var count = Math.min(80, Math.floor((W * H) / 12000));

    for (var i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * W,
            y: Math.random() * H,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            r: Math.random() * 2 + 1
        });
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);
        for (var i = 0; i < particles.length; i++) {
            var p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > W) p.vx *= -1;
            if (p.y < 0 || p.y > H) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.fill();

            for (var j = i + 1; j < particles.length; j++) {
                var p2 = particles[j];
                var dx = p.x - p2.x;
                var dy = p.y - p2.y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = 'rgba(255, 255, 255, ' + (0.08 * (1 - dist / 150)) + ')';
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }

            if (mouse.x !== null) {
                var mdx = p.x - mouse.x;
                var mdy = p.y - mouse.y;
                var mdist = Math.sqrt(mdx * mdx + mdy * mdy);
                if (mdist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = 'rgba(13, 110, 253, ' + (0.15 * (1 - mdist / 120)) + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }
    draw();
}

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

/* ─── Newsletter ─── */
function initNewsletter() {
    var btn = document.getElementById('btnNewsletter');
    if (!btn) return;
    btn.addEventListener('click', function () {
        Swal.fire({
            icon: 'success',
            title: '¡Suscrito!',
            text: 'Gracias por suscribirte a nuestro newsletter.',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
    });
}

/* ─── Search ─── */
function initSearch() {
    var input = document.getElementById('heroSearch');
    var results = document.getElementById('searchResults');
    var timer;
    if (!input || !results) return;

    input.addEventListener('input', function () {
        clearTimeout(timer);
        var q = this.value.trim();
        if (q.length < 2) { results.classList.remove('show'); return; }
        timer = setTimeout(function () { buscarPublicas(q); }, 400);
    });

    input.addEventListener('blur', function () {
        setTimeout(function () { results.classList.remove('show'); }, 300);
    });

    input.addEventListener('focus', function () {
        if (this.value.trim().length >= 2) results.classList.add('show');
    });
}

async function buscarPublicas(q) {
    var results = document.getElementById('searchResults');
    try {
        var res = await fetch('/api/publicas?q=' + encodeURIComponent(q));
        var data = await res.json();
        results.classList.add('show');
        results.innerHTML = '<div class="search-item bg-light bg-opacity-50 fw-semibold small">Resultados para "' + q + '"</div>';

        if (!data.success || data.data.length === 0) {
            results.innerHTML += '<div class="search-item text-muted small">Sin resultados.</div>';
            return;
        }

        var max = Math.min(data.data.length, 5);
        for (var i = 0; i < max; i++) {
            var p = data.data[i];
            var item = document.createElement('div');
            item.className = 'search-item';
            item.innerHTML = '<div class="search-title">' + escapeHtml(p.titulo) + '</div>' +
                '<div class="search-snippet">' + escapeHtml(p.contenido.substring(0, 80)) + '</div>';
            results.appendChild(item);
        }

        if (data.data.length > 5) {
            results.innerHTML += '<div class="search-item text-center small"><a href="/login" class="text-primary">Ver todos (' + data.data.length + ')</a></div>';
        }
    } catch (e) {
        results.innerHTML = '<div class="search-item text-danger small">Error al buscar.</div>';
    }
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
        renderTrending(data.data);
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
                    <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill">Noticia</span>\
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
        col.className = 'col-md-6';
        col.setAttribute('data-aos', 'fade-up');
        col.setAttribute('data-aos-delay', String((i % 3) * 100));

        var fecha = new Date(p.fecha_publicacion);
        var readingTime = Math.max(1, Math.ceil(p.contenido.length / 500));

        col.innerHTML = '\
            <div class="news-card cursor-pointer" onclick="window.location.href=\'/login\'" role="button">\
                ' + (p.imagen
                    ? '<img src="' + escapeHtml(p.imagen) + '" alt="' + escapeHtml(p.titulo) + '" class="card-img-top" loading="lazy">'
                    : '<div class="img-placeholder"><i class="bi bi-image"></i></div>'
                ) + '\
                <div class="card-body d-flex flex-column">\
                    <div class="d-flex gap-2 align-items-center mb-2">\
                        <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill" style="font-size:0.65rem;">Noticia</span>\
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

function renderTrending(posts) {
    var container = document.getElementById('trendingList');
    if (!container) return;

    container.innerHTML = '';
    var max = Math.min(posts.length, 5);

    for (var i = 0; i < max; i++) {
        var p = posts[i];
        var item = document.createElement('div');
        item.className = 'trending-item';
        item.setAttribute('onclick', "window.location.href='/login'");

        var numClass = 'top-' + (i + 1);
        if (i > 2) numClass = '';

        item.innerHTML = '\
            <div class="trending-number ' + numClass + '">' + (i + 1) + '</div>\
            <div class="flex-grow-1 min-w-0">\
                <div class="trending-title">' + escapeHtml(p.titulo) + '</div>\
                <div class="trending-meta mt-1">' + escapeHtml(p.nombre) + ' · ' + formatDate(new Date(p.fecha_publicacion)) + '</div>\
            </div>';
        container.appendChild(item);
    }

    if (max === 0) {
        container.innerHTML = '<div class="text-muted small text-center py-2">Sin tendencias aún.</div>';
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
            col.className = 'col-md-4';
            col.setAttribute('data-aos', 'fade-up');
            col.setAttribute('data-aos-delay', String(i * 100));

            var fecha = new Date(ev.fecha_evento);
            var meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            var diasSem = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

            col.innerHTML = '\
                <div class="event-card cursor-pointer" onclick="window.location.href=\'/login\'" role="button">\
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