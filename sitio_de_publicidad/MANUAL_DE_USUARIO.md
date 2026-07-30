# Manual de Usuario — Selva Sensorial

## Índice

1. [Introducción](#1-introducción)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [Acceso a la Plataforma](#3-acceso-a-la-plataforma)
4. [Navegación General](#4-navegación-general)
5. [Catálogo de Productos](#5-catálogo-de-productos)
6. [Carrito de Compras](#6-carrito-de-compras)
7. [Proceso de Pago](#7-proceso-de-pago)
8. [Mis Pedidos](#8-mis-pedidos)
9. [Panel de Administración](#9-panel-de-administración)
10. [Solución de Problemas](#10-solución-de-problemas)

---

## 1. Introducción

**Selva Sensorial** es una plataforma de comercio electrónico especializada en aromatizantes artesanales colombianos. Este manual describe todas las funcionalidades disponibles para usuarios y administradores.

---

## 2. Requisitos del Sistema

- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Conexión a Internet
- JavaScript habilitado
- Resolución mínima recomendada: 1024 × 768

---

## 3. Acceso a la Plataforma

### 3.1 Registro de Cuenta

1. Desde la página principal, haz clic en **"Registrarse"** (esquina superior derecha).
2. Completa el formulario:
   - **Nombre completo** (mínimo 3 caracteres)
   - **Correo electrónico** válido
   - **Contraseña** (mínimo 8 caracteres)
   - **Confirmar contraseña**
3. Haz clic en **"Crear Cuenta"**.
4. La sesión se iniciará automáticamente después del registro.

### 3.2 Inicio de Sesión

1. Haz clic en **"Iniciar sesión"**.
2. Ingresa tu **correo electrónico** y **contraseña**.
3. Haz clic en **"Iniciar Sesión"**.
4. Si olvidaste tus credenciales, contacta al administrador.

### 3.3 Recuperación de Acceso

- Tras 5 intentos fallidos, la cuenta se bloquea por 30 segundos.
- Para restablecer la contraseña, contacta al administrador del sistema.

---

## 4. Navegación General

### Barra de Navegación Superior

| Elemento | Descripción |
|---|---|
| **Logo** | Enlace a la página de inicio |
| **Inicio** | Página principal con productos destacados |
| **Productos** | Catálogo completo |
| **Sobre nosotros** | Información de la marca |
| **Contacto** | Información de contacto |
| **Carrito** | Icono del carrito de compras |
| **Iniciar sesión / Usuario** | Acceso a cuenta o menú de usuario |

### Menú de Usuario (sesión iniciada)

- **Editar perfil**: Modificar nombre, correo o contraseña
- **Mis Pedidos**: Historial de compras
- **Cerrar sesión**

---

## 5. Catálogo de Productos

### 5.1 Vista de Productos

- Los productos se muestran en cuadrícula con imagen, nombre, precio y stock.
- Los productos en oferta muestran una etiqueta **"Rebaja"**.
- Los productos agotados muestran el botón **"Agotado"** deshabilitado.

### 5.2 Detalle del Producto

Al hacer clic en un producto, puedes ver:

- Imagen del producto
- Nombre y descripción
- Precio (normal o rebajado)
- Stock disponible
- Características
- Especificaciones técnicas
- Selector de cantidad + botón **"Agregar al carrito"**

---

## 6. Carrito de Compras

### 6.1 Agregar Productos

1. Desde el catálogo o detalle del producto, haz clic en **"Agregar"** o **"Agregar al carrito"**.
2. Aparecerá una notificación de confirmación.
3. El icono del carrito mostrará el contador de productos.

### 6.2 Gestionar el Carrito

Abre el carrito desde el icono superior. Puedes:

- **Aumentar/disminuir** cantidad con los botones +/-
- **Eliminar** un producto con el icono de papelera
- Ver el **total** acumulado

### 6.3 Ir a Pagar

- Haz clic en **"Ir a pagar"**.
- Si no has iniciado sesión, se te pedirá que inicies sesión o te registres.
- Los productos del carrito se conservan al iniciar sesión.

---

## 7. Proceso de Pago

### 7.1 Datos de Envío

Completa el formulario con:

- **Nombre completo**
- **Correo electrónico**
- **Teléfono**
- **Dirección de envío**

### 7.2 Resumen del Pedido

Revisa los productos, cantidades, costo de envío y total.

- Envío **GRATIS** para pedidos superiores a $150.000 COP
- Costo de envío regular: $5.000 COP

### 7.3 Pago con Tarjeta

1. Ingresa los datos de la tarjeta (número, fecha de vencimiento, CVC).
2. Haz clic en **"Pagar"**.
3. Espera la confirmación del pago.

### 7.4 Confirmación

- Si el pago es exitoso, verás un resumen del pedido con número de referencia.
- Recibirás la confirmación en pantalla.
- El pedido quedará registrado en **"Mis Pedidos"**.

---

## 8. Mis Pedidos

### 8.1 Visualizar Pedidos

Desde el menú de usuario > **"Mis Pedidos"**, puedes ver:

- Lista de todos tus pedidos
- Estado actual de cada pedido
- Detalle de los productos comprados

### 8.2 Estados del Pedido

| Estado | Significado |
|---|---|
| **Pendiente** | Pedido recibido, en espera de procesamiento |
| **Enviado** | Pedido despachado |
| **Entregado** | Pedido recibido por el cliente |
| **Cancelado** | Pedido cancelado |

---

## 9. Panel de Administración

### 9.1 Acceso

- Inicia sesión con credenciales de administrador.
- Serás redirigido automáticamente al panel.

### 9.2 Secciones del Panel

#### Productos

- **Listado**: Todos los productos con nombre, categoría, precio, stock y estado.
- **Agregar**: Formulario para crear un nuevo producto.
  - Nombre, descripción, precio, categoría, stock, imagen
  - Especificaciones (clave: valor)
  - Características
  - Precio de rebaja (opcional)
- **Editar**: Modificar cualquier producto existente.
- **Eliminar**: Eliminar un producto (con confirmación).
- **Filtro por categoría**: Filtra productos por categoría.

#### Pedidos

- Lista de pedidos con referencia, cliente, total, estado y fecha.
- Cada pedido muestra los productos comprados.
- Los estados se actualizan manualmente.

#### Dashboard

- Resumen de ventas del día, semana y mes.
- Productos más vendidos.
- Pedidos por estado.
- Gráfico de ventas mensuales.

### 9.3 Gestión de Categorías

Las categorías disponibles son:

- **Aromatizantes**
- **Lociones**
- **Ambientadores**

---

## 10. Solución de Problemas

| Problema | Solución |
|---|---|
| **No carga la página** | Verifica tu conexión a Internet. Actualiza la página. |
| **No inicia sesión** | Verifica correo y contraseña. Espera 30 segundos si bloqueado. |
| **Carrito vacío al pagar** | Asegúrate de agregar productos antes de ir a pagar. Los productos se conservan al iniciar sesión. |
| **Error al pagar** | Verifica los datos de la tarjeta. Contacta a tu banco. |
| **No veo mis pedidos** | Asegúrate de haber iniciado sesión con la cuenta correcta. |
| **Página lenta** | Actualiza la página. Limpia la caché del navegador. |
| **Error 500** | Contacta al administrador del sistema. |

---

## Contacto de Soporte

- **Correo**: apomat@gmail.com
- **Teléfono**: 312 732 0463
- **Dirección**: Carrera 16 # 12-165, barrio La Yesquita, Quibdó, Chocó.

---

*Documento generado para Selva Sensorial — Última actualización: Julio 2026*
