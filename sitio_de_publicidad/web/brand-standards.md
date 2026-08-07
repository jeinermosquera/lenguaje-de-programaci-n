# Brand Standards — Apomat

> Dirección estética: **Selva Sensorial**
> Fecha: Julio 2026

---

## 1. Paleta de color

| Variable              | Hex       | Propósito                                                    |
|-----------------------|-----------|--------------------------------------------------------------|
| `--color-ebano`       | `#2C2925` | Fondos oscuros (navbar, footer, botones primarios)           |
| `--color-lino`        | `#E8E3DA` | Fondo general de página (`--bg`) y hero (`--hero-bg`)        |
| `--color-arcilla`     | `#D9CFC0` | Fondos alternos (about, secciones secundarias)               |
| `--color-oro`         | `#C49B4A` | Acentos dorados (hover, íconos, badges, bordes decorativos)  |
| `--color-hueso`       | `#F5F1EB` | Fondos de tarjetas, inputs, superficies elevadas             |
| `--color-texto`       | `#2C2C2C` | Texto principal                                              |
| `--color-texto-suave` | `#7A7A7A` | Texto secundario, metadatos, placeholders                    |

### Propósito de cada color

- **Ébano** — Representa la tierra húmeda del Chocó. Se usa en elementos que necesitan anclaje visual: navbar, footer, botones CTA.
- **Lino** — Base luminosa y serena que evoca textiles naturales. Fondo principal del sitio.
- **Arcilla** — Techo visual entre la tierra y la luz. Ideal para separar secciones sin contraste agresivo.
- **Oro** — El sol filtrado por el dosel de la selva. Solo para detalles que merecen atención: hover states, íconos, líneas decorativas.
- **Hueso** — Superficie limpia y táctil. Tarjetas, formularios, modales.
- **Texto** — Contraste legible sin llegar al negro puro.
- **Texto suave** — Información secundaria sin competir con el contenido principal.

---

## 2. Escala tipográfica

### Display — `var(--font-brand)` (Cormorant Garamond)

| Uso                        | Tamaño  | Peso  | Tracking  | Line-height |
|----------------------------|---------|-------|-----------|-------------|
| Hero heading (`h1`)        | 3.8rem  | 600   | 0.01em    | 1.08        |
| Section title              | 2.6rem  | 600   | normal    | 1.15        |
| PDP title                  | 2.6rem  | 600   | -0.01em   | 1.12        |
| Footer brand               | 1.3rem  | 600   | normal    | 1.2         |
| Contact subtitle           | 1.4rem  | 600   | normal    | 1.2         |

### Body — `var(--font-body)` (Poppins)

| Uso                        | Tamaño  | Peso  | Tracking  |
|----------------------------|---------|-------|-----------|
| Nav links                  | 0.82rem | 500   | 0.08em    |
| Hero subhead               | 1.15rem | 300   | normal    |
| Body text                  | 1rem    | 400   | normal    |
| Product card title         | 0.85rem | 500   | 0.02em    |
| Button text                | 0.85rem | 500   | 0.06em    |
| Small / meta               | 0.82rem | 400   | normal    |
| Eyebrow / label            | 0.68rem | 500   | 0.18em    |

### Utility

| Uso                        | Tamaño  | Peso  | Tracking  |
|----------------------------|---------|-------|-----------|
| Price                      | 0.88rem | 500   | 0.01em    |
| Cart badge                 | 0.65rem | 700   | normal    |
| Toast / alert              | 0.8rem  | 400   | normal    |

---

## 3. Reglas de uso (qué no hacer)

1. **No usar el oro como color de fondo** — El oro es un acento. Nunca como relleno de áreas grandes.
2. **No mezclar más de dos tonos de la paleta en un mismo bloque** — Máximo dos colores por componente (ej. fondo ébano + texto blanco + acento oro).
3. **No aplicar tracking a textos display** — Cormorant Garamond solo lleva tracking en hero (0.01em), nunca en títulos de sección o encabezados.
4. **No usar mayúsculas sostenidas en body copy** — Solo en nav-links, botones y etiquetas pequeñas (eyebrow).
5. **No saturar de "Hilos de Oro"** — Máximo uno por sección. Es un elemento de apertura, no decorativo recurrente.
6. **No someter el logo a rotación, cambio de color o deformación** — El brand mark siempre en su versión original. En fondos oscuros: invertido a blanco. En fondos claros: versión original.

---

## 4. Tono de voz de Apomat

Apomat habla **como un artesano que recibe a alguien en su taller**: cálido, presente, con orgullo silencioso.

| Principio         | Descripción                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| Sensorial         | Priorizar verbos y sustantivos que evoquen los sentidos: *"creamos atmósferas", "capturar la esencia", "experiencias olfativas"* |
| Auténtico         | Sin superlativos vacíos. Preferir *"ingredientes naturales seleccionados a mano"* sobre *"los mejores ingredientes"* |
| Cercano           | Tratar al usuario de *"tú"*. Frases cortas. Sin jerga técnica.              |
| Con arraigo       | Mencionar el origen colombiano (Chocó) con naturalidad, no como eslogan.    |
| Visual            | Preferir mostrar a decir. El copy debe apoyar la imagen, no competir con ella. |

### Ejemplos de copy aprobado

- Hero: *"No solo perfumamos espacios, creamos atmósferas."*
- About: *"Somos una marca colombiana apasionada por capturar la esencia de los paisajes que nos rodean."*
- Tagline footer: *"Aromatizantes que transforman tus espacios en experiencias olfativas únicas."*

---

## 5. Signature element — "Hilo de Oro"

### Qué es

Una línea horizontal delgada de color oro que antecede visualmente a los títulos de sección. Representa el hilo de la tradición artesanal que conecta cada parte de la marca.

### Código

```css
.section-eyebrow {
  display: block;
  width: 80px;
  height: 1.5px;
  background: var(--color-oro);
  margin: 0 auto 1.2rem;
  border-radius: 2px;
}
```

### Reglas de uso

1. **Ubicación**: siempre antes del `<h1>` o `<h2>` de la sección, centrado.
2. **Cantidad**: una sola instancia por sección.
3. **No clickeable**: es puramente decorativo. No debe llevar `href` ni eventos.
4. **En hover de tarjetas**: puede animarse (ensancharse de 80px → 100px) como micro-interacción.
5. **No reemplazar** con íconos, emojis o imágenes.

### Estados animados (opcional)

```css
.product-card:hover .section-eyebrow {
  width: 100px;
  transition: width 0.4s ease;
}
```
