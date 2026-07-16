# Apomat — E-commerce de aromas ambientales

Plataforma web de comercio electrónico para la venta de difusores de aroma artesanales colombianos. Incluye catálogo de productos, carrito de compras, pagos integrados con Stripe, panel de administración y seguimiento de pedidos.

---

## Stack tecnológico

### Backend
- **Python 3 + Flask** — framework web (servidor WSGI, rutas, sesiones)
- **mysql.connector** — conexión directa a MySQL desde Python
- **Werkzeug** — generación y verificación de hashes de contraseñas
- **Stripe SDK** — creación de PaymentIntents y verificación de webhooks
- **Base de datos:** MySQL (`jeiner_db` en `127.0.0.1`, usuario `root`)

### Frontend
- **HTML5 + CSS3** — 8 páginas: login, dashboard, productos, detalle, checkout, mis pedidos, éxito, fallo
- **Bootstrap 5.3.3** (CDN) — sistema de grillas, navbar, offcanvas, modales, dropdowns
- **Bootstrap Icons 1.11.3** (CDN)
- **Google Fonts** — Cormorant Garamond (títulos) + Poppins (cuerpo)
- **SweetAlert2** (CDN) — notificaciones toast, confirmaciones, alertas
- **Stripe.js v3** — Elements (campo de tarjeta embebido) + confirmCardPayment
- **CSS propio** — modular en `web/css/` (style.css, productos.css, checkout.css, admin.css, mis-pedidos.css, pedido-exitoso.css, pedido-fallido.css)
- **JavaScript propio** — `web/js/carrito.js` (objeto `Carrito` con localStorage)

### Entorno
- XAMPP (Apache + MySQL), Flask en puerto 5000
- Node.js (solo para Bootstrap como dependencia dev, `package.json`)
- Stripe en modo test

---

## Estructura del proyecto

```
sitio_de_publicidad/
├── app.py                   # Aplicación Flask (~1020 líneas)
├── package.json             # Dependencia: bootstrap
├── login/                   # Página de login/registro
│   ├── index.html
│   ├── css/                 # Estilos del login
│   ├── img/                 # bg-login.jpg, logo-apomat.png
│   └── favicon/
├── web/                     # Sitio protegido (requiere sesión)
│   ├── index.html           # Dashboard / inicio
│   ├── productos.html       # Catálogo de productos
│   ├── producto.html        # Detalle individual
│   ├── checkout.html        # Pago con Stripe Elements
│   ├── mis-pedidos.html     # Historial del usuario
│   ├── pedido-exitoso.html  # Confirmación de pago
│   ├── pedido-fallido.html  # Pago rechazado
│   ├── admin.html           # Panel administrador
│   ├── css/                 # Estilos modulares
│   │   ├── style.css        # Global (navbar, hero, cards, footer, carrito, etc.)
│   │   ├── productos.css    # Catálogo
│   │   ├── checkout.css     # Checkout
│   │   ├── admin.css        # Panel admin
│   │   ├── mis-pedidos.css  # Historial
│   │   ├── pedido-exitoso.css
│   │   └── pedido-fallido.css
│   ├── js/
│   │   └── carrito.js       # Lógica del carrito (localStorage)
│   ├── img/                 # Imágenes de productos
│   └── favicon/
└── node_modules/
```

---

## Base de datos

### Tabla: `usuario`
| Campo | Tipo |
|---|---|
| id | INT AUTO_INCREMENT PK |
| nombre | VARCHAR(100) |
| correo | VARCHAR(100) UNIQUE |
| contrasena | VARCHAR(255) — hash Werkzeug |

### Tabla: `producto`
| Campo | Tipo |
|---|---|
| id | INT AUTO_INCREMENT PK |
| nombre | VARCHAR(150) |
| imagen | VARCHAR(255) |
| precio | INT |
| descripcion | TEXT |
| caracteristicas | TEXT (JSON array) |
| especificaciones | TEXT (JSON array) |
| disponible | TINYINT DEFAULT 1 |
| precio_rebaja | INT DEFAULT NULL |
| stock | INT DEFAULT 0 |

### Tabla: `pedido`
| Campo | Tipo |
|---|---|
| id | INT AUTO_INCREMENT PK |
| usuario_id | INT FK → usuario(id) |
| referencia | VARCHAR(100) UNIQUE |
| total | INT |
| estado | VARCHAR(30) — pendiente / pagado / enviado / entregado / cancelado |
| nombre, email, telefono, direccion | datos del comprador |
| fecha | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |

### Tabla: `detalle_pedido`
| Campo | Tipo |
|---|---|
| id | INT AUTO_INCREMENT PK |
| pedido_id | INT FK → pedido(id) ON DELETE CASCADE |
| producto_id | INT FK → producto(id) |
| nombre_producto | VARCHAR(150) |
| precio | INT |
| cantidad | INT |

### Tabla: `contacto`
| Campo | Tipo |
|---|---|
| id | INT AUTO_INCREMENT PK |
| nombre | VARCHAR(100) |
| correo | VARCHAR(100) |
| mensaje | TEXT |
| fecha | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |

---

## Rutas de la API

### Públicas
| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Login/registro |
| `/register` | POST | Registrar usuario |
| `/login` | POST | Iniciar sesión |
| `/logout` | GET | Cerrar sesión |
| `/css/<path>` | GET | CSS login |
| `/img/<path>` | GET | Imágenes login |

### Protegidas (requiere sesión)
| Ruta | Método | Descripción |
|---|---|---|
| `/dashboard` | GET | Inicio del sitio |
| `/productos` | GET | Catálogo |
| `/producto/<id>` | GET | Detalle producto |
| `/checkout` | GET | Página de pago |
| `/pedido-exitoso` | GET | Confirmación |
| `/pedido-fallido` | GET | Pago fallido |
| `/mis-pedidos` | GET | Historial del usuario |
| `/api/productos` | GET | Listar productos (JSON) |
| `/api/producto/<id>` | GET | Detalle producto (JSON) |
| `/api/checkout` | POST | Crear PaymentIntent + pedido |
| `/api/mis-pedidos` | GET | Pedidos del usuario (JSON) |
| `/enviar-contacto` | POST | Enviar formulario de contacto |
| `/site/css/<path>` | GET | CSS del sitio |
| `/site/img/<path>` | GET | Imágenes del sitio |
| `/site/js/<path>` | GET | JS del sitio |

### Gestión de cuenta
| Ruta | Método | Descripción |
|---|---|---|
| `/usuario` | GET | Datos del usuario logueado |
| `/api/usuario/editar` | POST | Cambiar nombre y correo |
| `/api/usuario/cambiar-contrasena` | POST | Cambiar contraseña |
| `/api/usuario/eliminar` | POST | Eliminar cuenta y datos |

### Administración (requiere admin)
| Ruta | Método | Descripción |
|---|---|---|
| `/admin` | GET | Panel admin |
| `/admin/api/productos` | GET | Todos los productos (JSON) |
| `/admin/productos/agregar` | POST | Crear producto |
| `/admin/productos/editar/<id>` | POST | Editar precio/stock/rebaja |
| `/admin/productos/eliminar/<id>` | POST | Eliminar producto |
| `/admin/productos/toggle/<id>` | POST | Activar/desactivar disponible |
| `/admin/api/pedidos` | GET | Todos los pedidos con items (JSON) |
| `/admin/api/pedidos/estado/<id>` | POST | Cambiar estado del pedido |

### Webhook
| Ruta | Método | Descripción |
|---|---|---|
| `/api/stripe/webhook` | POST | Escucha `payment_intent.succeeded` |

---

## Flujo de pago

1. Usuario agrega productos al carrito (almacenado en `localStorage`)
2. En `/checkout` llena datos de envío y tarjeta
3. `POST /api/checkout` crea un `PaymentIntent` en Stripe (monto × 100 para COP) y registra el pedido en BD con estado `pendiente`, descontando stock
4. El frontend llama a `stripe.confirmCardPayment()` con el `client_secret` recibido
5. Si el pago es exitoso → redirige a `/pedido-exitoso`; si falla → redirige a `/pedido-fallido` (con restauración del carrito desde backup)
6. Stripe envía webhook `payment_intent.succeeded` → `/api/stripe/webhook` actualiza estado a `pagado`

---

## Administración

El admin (correo: `apomat@gmail.com`, contraseña configurable) tiene acceso a:

- **Productos:** CRUD completo, toggle de disponibilidad, editar precio/rebaja/stock
- **Pedidos:** listado con filtro (Pendientes / Todos), cambio de estado vía dropdown en línea (pendiente → pagado → enviado → entregado / cancelado), colores indicativos por estado

### Estados de pedido y colores
| Estado | Color |
|---|---|
| Pendiente | Amarillo |
| Pagado | Azul claro |
| Enviado | Azul |
| Entregado | Verde |
| Cancelado | Rojo |

---

## Diseño visual

- **Paleta:** Azul marino (`#1c2e4a`), dorado (`#c9960e`), crema (`#f5f0e8`)
- **Tipografía:** Cormorant Garamond (serif editorial) + Poppins (sans-serif limpia)
- **Componentes:** tarjetas redondeadas de 20px, sombras suaves, botones pill, animaciones en hover
- **Navegación:** sticky navbar con degradado azul cielo, offcanvas oscuro en móvil, carrito en offcanvas lateral

---

## Instalación y ejecución

### Requisitos
- Python 3.10+
- XAMPP (MySQL en `127.0.0.1:3306`)
- Node.js (para Bootstrap, opcional)

### Pasos
```bash
# 1. Clonar repositorio
git clone <repo-url>
cd sitio_de_publicidad

# 2. Instalar dependencias Python
pip install flask mysql-connector-python werkzeug stripe

# 3. Instalar Bootstrap (opcional, para compilar SCSS)
npm install

# 4. Iniciar Apache + MySQL (XAMPP)

# 5. Ejecutar la app
python app.py
```

La app crea automáticamente las tablas y siembra 8 productos iniciales al primer arranque.

Servidor en `http://127.0.0.1:5000`.

### Stripe
Reemplazar `STRIPE_WEBHOOK_SECRET` en `app.py` con el secreto real del webhook en producción. Las claves actuales son de modo test.
