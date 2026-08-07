# Apomat — E-commerce de aromas ambientales

Plataforma web de comercio electrónico para la venta de difusores de aroma artesanales colombianos. Incluye catálogo de productos, carrito de compras, pagos integrados con Stripe (3 campos separados), panel de administración y seguimiento de pedidos con envío incluido.

---

## Stack tecnológico

### Backend
- **Python 3 + Flask** — framework web (servidor WSGI, rutas, sesiones)
- **mysql.connector** — conexión directa a MySQL desde Python
- **Werkzeug** — generación y verificación de hashes de contraseñas
- **Stripe SDK** — creación de PaymentIntents y verificación de webhooks
- **python-dotenv** — carga de variables de entorno desde `.env`
- **Base de datos:** MySQL (`jeiner_db` en `127.0.0.1`, usuario `root`)

### Frontend
- **HTML5 + CSS3** — 9 páginas: login, dashboard, productos, detalle, checkout, mis pedidos, admin, éxito, fallo
- **Bootstrap 5.3.3** (CDN) — sistema de grillas, navbar, offcanvas, modales, dropdowns
- **Bootstrap Icons 1.11.3** (CDN)
- **Google Fonts** — Cormorant Garamond (títulos) + Poppins (cuerpo)
- **SweetAlert2** (CDN) — notificaciones toast, confirmaciones, alertas
- **Stripe.js v3** — Elements (3 campos separados: cardNumber, cardExpiry, cardCvc) + confirmCardPayment
- **CSS propio** — modular en `web/css/` (7 archivos)
- **JavaScript propio** — `web/js/carrito.js` (objeto `Carrito` con localStorage aislado por usuario)

### Entorno
- XAMPP (Apache + MySQL), Flask en puerto 5000
- Node.js (solo para Bootstrap como dependencia dev, `package.json`)
- Stripe en modo test (tarjeta de prueba: `4242 4242 4242 4242`)

---

## Estructura del proyecto

```
sitio_de_publicidad/
├── app.py                   # Aplicación Flask (~1014 líneas, 34 rutas)
├── .env                     # Variables de entorno (Stripe keys, ignorado por git)
├── package.json             # Dependencia: bootstrap
├── login/                   # Página pública de login/registro
│   ├── index.html           #   Login + Register con tabs
│   ├── css/style.css        #   Estilos (split layout, 278 líneas)
│   ├── img/                 #   bg-login.jpg, logo-apomat.png, img-1.png
│   └── favicon/             #   Favicon en múltiples tamaños
├── web/                     # Sitio protegido (requiere sesión)
│   ├── index.html           #   Dashboard / inicio con productos destacados dinámicos
│   ├── productos.html       #   Catálogo completo de productos
│   ├── producto.html        #   Detalle individual con selector de cantidad
│   ├── checkout.html        #   Pago con Stripe Elements (3 campos separados)
│   ├── mis-pedidos.html     #   Historial del usuario con productos desglosados
│   ├── pedido-exitoso.html  #   Confirmación de pago exitoso
│   ├── pedido-fallido.html  #   Pago rechazado con restauración de carrito
│   ├── admin.html           #   Panel administrador (productos + pedidos)
│   ├── css/                 #   Estilos modulares
│   │   ├── style.css        #     Global (1083 líneas)
│   │   ├── productos.css    #     Catálogo (40 líneas)
│   │   ├── checkout.css     #     Checkout con 3 campos Stripe (106 líneas)
│   │   ├── admin.css        #     Panel admin (21 líneas)
│   │   ├── mis-pedidos.css  #     Historial (17 líneas)
│   │   ├── pedido-exitoso.css  #   Éxito (10 líneas)
│   │   └── pedido-fallido.css  #   Fallo (10 líneas)
│   ├── js/
│   │   └── carrito.js       #   Lógica del carrito (localStorage aislado por usuario)
│   ├── img/                 #   Imágenes de productos y logo
│   └── favicon/             #   Favicon del sitio
└── node_modules/
```

---

## Base de datos (MySQL `jeiner_db`)

### Tabla: `usuario`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identificador único |
| nombre | VARCHAR(100) | Nombre completo del usuario |
| correo | VARCHAR(100) UNIQUE | Correo electrónico |
| contrasena | VARCHAR(255) | Hash generado con Werkzeug |

### Tabla: `producto`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identificador único |
| nombre | VARCHAR(150) | Nombre del producto |
| imagen | VARCHAR(255) | Nombre del archivo de imagen en `web/img/` |
| precio | INT | Precio en COP |
| descripcion | TEXT | Descripción del producto |
| caracteristicas | TEXT | Array JSON de características |
| especificaciones | TEXT | Array JSON de especificaciones |
| disponible | TINYINT DEFAULT 1 | 1=visible, 0=oculto |
| precio_rebaja | INT DEFAULT NULL | Precio rebajado (NULL sin rebaja) |
| stock | INT DEFAULT 0 | Cantidad disponible |

### Tabla: `pedido`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identificador único |
| usuario_id | INT FK → usuario(id) | Usuario que realizó el pedido |
| referencia | VARCHAR(100) UNIQUE | Código único (ej. APOMAT-1234567890-1) |
| total | INT | Total en COP (productos + envío) |
| costo_envio | INT DEFAULT 0 | Costo de envío en COP |
| estado | VARCHAR(30) | pendiente, enviado, entregado, cancelado |
| nombre | VARCHAR(150) | Nombre del comprador |
| email | VARCHAR(150) | Correo del comprador |
| telefono | VARCHAR(30) | Teléfono de contacto |
| direccion | TEXT | Dirección de envío |
| fecha | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Fecha del pedido |

### Tabla: `detalle_pedido`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identificador único |
| pedido_id | INT FK → pedido(id) ON DELETE CASCADE | Pedido al que pertenece |
| producto_id | INT FK → producto(id) | Producto comprado |
| nombre_producto | VARCHAR(150) | Nombre en el momento de la compra |
| precio | INT | Precio unitario en COP |
| cantidad | INT | Cantidad comprada |

### Tabla: `contacto`
| Campo | Tipo | Descripción |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identificador único |
| nombre | VARCHAR(100) | Nombre del remitente |
| correo | VARCHAR(100) | Correo del remitente |
| mensaje | TEXT | Mensaje enviado |
| fecha | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Fecha de envío |

---

## Configuración de entorno (`.env`)

Crear archivo `.env` en la raíz del proyecto:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

El backend lee estas claves con `os.getenv()` y tiene fallback a placeholders si no existen. El archivo `.env` está en `.gitignore` para no exponer credenciales.

---

## API completa (34 rutas)

### Archivos estáticos públicos
| Ruta | Método | Sirve desde | Descripción |
|---|---|---|---|
| `/` | GET | `login/index.html` | Página de login/registro |
| `/css/<path:filename>` | GET | `login/css/` | CSS del login |
| `/img/<path:filename>` | GET | `login/img/` | Imágenes del login |
| `/favicon/<path:filename>` | GET | `login/favicon/` | Favicon del login |
| `/static/img/<path:filename>` | GET | `static/img/` | Imágenes estáticas (opcional) |

### Archivos estáticos protegidos
| Ruta | Método | Sirve desde | Descripción |
|---|---|---|---|
| `/site/css/<path:filename>` | GET | `web/css/` | CSS del sitio |
| `/site/img/<path:filename>` | GET | `web/img/` | Imágenes del sitio |
| `/site/js/<path:filename>` | GET | `web/js/` | JavaScript del sitio |
| `/site/favicon/<path:filename>` | GET | `web/favicon/` | Favicon del sitio |

### Autenticación
| Ruta | Método | Parámetros | Descripción |
|---|---|---|---|
| `/register` | POST | `full_name`, `email`, `password` | Registra usuario, auto-login, redirige a dashboard/admin |
| `/login` | POST | `email`, `password` | Inicia sesión, redirige a dashboard/admin |
| `/logout` | GET | — | Limpia sesión, redirige a `/` |

### Páginas protegidas (requiere sesión)
| Ruta | Método | Descripción |
|---|---|---|
| `/dashboard` | GET | Inicio con productos destacados dinámicos |
| `/productos` | GET | Catálogo completo |
| `/producto/<int:id>` | GET | Detalle de producto |
| `/checkout` | GET | Página de pago con Stripe |
| `/mis-pedidos` | GET | Historial del usuario |
| `/pedido-exitoso` | GET | Confirmación de pago |
| `/pedido-fallido` | GET | Pago fallido |
| `/admin` | GET | Panel de administración (solo admin) |

### API de datos (JSON)
| Ruta | Método | Parámetros | Respuesta | Descripción |
|---|---|---|---|---|
| `/api/productos` | GET | — | Array de productos | Lista todos los productos |
| `/api/producto/<int:id>` | GET | — | Objeto producto | Detalle de un producto |
| `/usuario` | GET | — | `{id, nombre, email, admin}` | Datos del usuario logueado |
| `/api/mis-pedidos` | GET | — | Array de pedidos con items | Pedidos del usuario |
| `/api/checkout` | POST | JSON: `nombre, email, telefono, direccion, items, total, costo_envio` | `{client_secret, referencia}` | Crea PaymentIntent + pedido |

### Gestión de cuenta (JSON)
| Ruta | Método | Parámetros | Descripción |
|---|---|---|---|
| `/api/usuario/editar` | POST | JSON: `{nombre, email}` | Actualiza nombre y correo |
| `/api/usuario/cambiar-contrasena` | POST | JSON: `{actual, nueva}` | Cambia contraseña |
| `/api/usuario/eliminar` | POST | — | Elimina cuenta y datos asociados |

### Formulario de contacto
| Ruta | Método | Parámetros | Descripción |
|---|---|---|---|
| `/enviar-contacto` | POST | `nombre, email, mensaje` | Guarda mensaje en BD y redirige |

### Administración (solo admin)
| Ruta | Método | Parámetros | Descripción |
|---|---|---|---|
| `/admin/api/productos` | GET | — | Todos los productos (JSON) |
| `/admin/productos/agregar` | POST | form + imagen | Crea nuevo producto |
| `/admin/productos/editar/<int:id>` | POST | form: `precio, precio_rebaja, stock` | Edita precio/stock/rebaja |
| `/admin/productos/eliminar/<int:id>` | POST | — | Elimina producto y su imagen |
| `/admin/productos/toggle/<int:id>` | POST | — | Activa/desactiva disponible |
| `/admin/api/pedidos` | GET | — | Todos los pedidos con items (JSON) |
| `/admin/api/pedidos/estado/<int:id>` | POST | form: `estado` | Cambia estado del pedido |

### Webhook Stripe
| Ruta | Método | Descripción |
|---|---|---|
| `/api/stripe/webhook` | POST | Escucha `payment_intent.succeeded` y actualiza estado |

---

## Funciones del backend (`app.py`)

### Funciones auxiliares
| Función | Descripción |
|---|---|
| `inicializar_base_datos()` | Crea/actualiza tablas `producto`, `pedido`, `detalle_pedido`, `contacto`. Agrega columnas `precio_rebaja`, `stock`, `costo_envio` si no existen. |
| `get_connection()` | Retorna conexión a MySQL (`127.0.0.1:3306/jeiner_db`, root sin contraseña) |
| `producto_db_a_dict(row)` | Convierte tupla de BD a dict con `precio_formateado`, `precio_rebaja_formateado`, `en_rebaja`, `stock` |
| `add_header(response)` | `@app.after_request` — desactiva caché del navegador |

### Manejadores de rutas (27 funciones)
Cada ruta listada en la sección anterior tiene su función manejadora correspondiente en `app.py`. Las rutas protegen el acceso verificando `session["logueado"]` y `session["admin"]` según corresponda.

---

## Funciones del frontend (`web/js/carrito.js`)

### Objeto `Carrito`

| Método | Parámetros | Descripción |
|---|---|---|
| `getItems()` | — | Lee carrito de `localStorage` (clave `"apomat_carrito"`) |
| `setItems(items)` | `items` (array) | Guarda carrito y actualiza badge + offcanvas |
| `agregar(producto, cantidad)` | `producto` (obj), `cantidad` (int) | Agrega producto o incrementa cantidad |
| `eliminar(id)` | `id` (number) | Elimina producto del carrito |
| `actualizarCantidad(id, cantidad)` | `id`, `cantidad` (int) | Cambia cantidad; si <= 0 elimina |
| `vaciar()` | — | Limpia carrito y backup |
| `getTotal()` | — | Suma (precio × cantidad) de todos los items |
| `getCantidadTotal()` | — | Cantidad total de unidades |
| `formatearPrecio(precio)` | `precio` (number) | Formato COP: `"$ 1.234"` |
| `actualizarBadge()` | — | Actualiza contador en navbar |
| `renderizarOffcanvas()` | — | Renderiza carrito en offcanvas |

### Funciones globales
| Función | Descripción |
|---|---|
| `mostrarToastCarrito(nombre)` | SweetAlert2 toast: "{nombre} — Agregado al carrito" |
| `DOMContentLoaded` | Al cargar: verifica si el usuario cambió (comparando `apomat_cart_user` con `sessionStorage`) y limpia carrito si es otro usuario |

---

## Detalle de los cambios implementados

### 1. Checkout con 3 campos Stripe separados
- `web/checkout.html`: formulario con 3 elementos Stripe individuales (cardNumber, cardExpiry, cardCvc)
- `web/css/checkout.css`: estilos independientes para cada campo, con estados focus/invalid
- Permite mejor control visual y validación por campo

### 2. Costo de envío
- **$5,000 COP** fijo para pedidos menores a $150,000 COP
- **Gratis** para pedidos de $150,000 COP o más
- Se muestra en el resumen del checkout, se guarda en BD (`pedido.costo_envio`) y se visualiza en admin y mis-pedidos

### 3. Carrito aislado por usuario
- Almacenado en `localStorage` con clave `"apomat_carrito"`
- Se guarda el ID del usuario en `sessionStorage` (`"apomat_cart_user"`)
- Si el usuario actual es diferente al que tenía el carrito, se limpia automáticamente

### 4. Productos dinámicos desde BD
- Los 4 productos destacados del inicio se cargan vía `/api/productos` y se filtran con `.filter(p => p.disponible).slice(0, 4)`
- Productos hardcodeados eliminados de `app.py`

### 5. Estados de pedido
| Estado | Color | Descripción |
|---|---|---|
| Pendiente | Amarillo | Pedido creado, pago recibido |
| Enviado | Azul | Pedido despachado |
| Entregado | Verde | Pedido recibido por el cliente |
| Cancelado | Rojo | Pedido cancelado |

### 6. Fechas en español
Formato: "16 de julio de 2026". Implementado con arrays de meses/días en español en el frontend.

### 7. Productos por fila en admin y mis-pedidos
- Cada producto aparece como fila separada en la tabla
- Columnas: producto, precio unitario, cantidad, subtotal

### 8. "Mis Pedidos" en menú desplegable
- Enlace movido de la barra de navegación al menú desplegable del usuario (en todas las páginas)

---

## Flujo de pago

1. Usuario navega productos → agrega al carrito (almacenado en `localStorage` aislado por usuario)
2. En `/checkout` completa 2 pasos:
   - **Paso 1**: datos personales (nombre, email, teléfono, dirección)
   - **Paso 2**: datos de tarjeta (3 campos Stripe separados) y resumen con envío calculado
3. `POST /api/checkout`:
   - Crea `PaymentIntent` en Stripe (monto × 100, moneda COP)
   - Inserta pedido en BD con estado `pendiente` y `costo_envio`
   - Inserta cada producto como fila en `detalle_pedido`
   - Descuenta stock de cada producto
4. Frontend llama a `stripe.confirmCardPayment()` con el `client_secret`
5. Éxito → redirige a `/pedido-exitoso?referencia=...` (limpia carrito)
6. Fallo → redirige a `/pedido-fallido` (restaura carrito desde backup en localStorage)
7. Webhook `payment_intent.succeeded` → actualiza estado vía `/api/stripe/webhook`

---

## Administración

El admin (correo: `apomat@gmail.com`) tiene acceso a `/admin` con:

### Productos
- **CRUD completo**: agregar, editar (precio, stock, rebaja), eliminar
- **Toggle de disponibilidad**: activar/desactivar visibilidad en tienda
- **Imagen**: subida de archivo con nombre único (timestamp + filename)

### Pedidos
- Listado completo con datos del cliente y productos desglosados
- **Filtro**: Pendientes / Todos
- **Cambio de estado**: dropdown inline por cada pedido
- **Estados**: pendiente, enviado, entregado, cancelado

---

## Diseño visual

### Paleta de colores
```css
--navy:       #1c2e4a    /* Azul marino oscuro */
--navy-soft:  #2c3e5e    /* Azul marino suave */
--cream:      #f5f0e8    /* Crema */
--blue:       #4a90d9    /* Azul claro */
--gold-dark:  #a67c00    /* Dorado oscuro */
--gold:       #c9960e    /* Dorado */
--gold-light: #d4a92a    /* Dorado claro */
--ink:        #2d2d2d    /* Texto oscuro */
--text-muted: #6c757d    /* Texto secundario */
```

### Tipografía
- Títulos: **Cormorant Garamond** (serif editorial, 500/600 weight)
- Cuerpo: **Poppins** (sans-serif limpia, 300/400/500/600 weight)

### Componentes
- Tarjetas redondeadas (20px border-radius), sombras suaves
- Botones pill (50px border-radius) con hover animation
- Sticky navbar con degradado azul cielo
- Offcanvas oscuro en móvil, carrito en offcanvas lateral
- Hero full-viewport con overlay gradient
- Grid responsive de productos (4 columnas → 2 → 1)

---

## Instalación y ejecución

### Requisitos
- Python 3.10+
- XAMPP (MySQL en `127.0.0.1:3306`)
- Node.js (opcional, para Bootstrap)

### Pasos
```bash
# 1. Clonar repositorio
git clone <repo-url>
cd sitio_de_publicidad

# 2. Instalar dependencias Python
pip install flask mysql-connector-python werkzeug stripe python-dotenv

# 3. Configurar variables de entorno
# Crear .env con:
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_PUBLISHABLE_KEY=pk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...

# 4. Instalar Bootstrap (opcional)
npm install

# 5. Iniciar Apache + MySQL (XAMPP)

# 6. Ejecutar la app
python app.py
```

El servidor inicia en `http://127.0.0.1:5000`.

### Stripe (modo test)
- Claves se leen desde `.env`
- Tarjeta de prueba: `4242 4242 4242 4242` (cualquier fecha futura, cualquier CVC)
- Reemplazar `STRIPE_WEBHOOK_SECRET` con el secreto real del webhook en producción

### Notas
- La app crea automáticamente las tablas al primer arranque
- Los productos deben agregarse desde el panel admin (`/admin`)
- Admin por defecto: `apomat@gmail.com` (registrarse con ese correo otorga permisos de admin)
- Puerto 5000, debug mode activado
