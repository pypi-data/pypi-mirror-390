# Guía de Migración y Nuevas Características - KardoCSS

## Versión: 1.0 (Lanzamiento con Sistema Responsive)

Esta guía describe las nuevas características y cambios introducidos en la última versión de KardoCSS. El cambio más importante es la **implementación completa del sistema responsive mobile-first**.

---

## 🚀 Nuevas Características Principales

### 1. Sistema Responsive Completo

KardoCSS ahora es un framework completamente responsive y mobile-first. Todas las utilidades principales tienen variantes para los siguientes breakpoints:

| Prefijo | Breakpoint | Descripción |
|---|---|---|
| `sm:` | `640px` | Teléfonos grandes / Tablets pequeñas |
| `md:` | `768px` | Tablets |
| `lg:` | `1024px` | Laptops |
| `xl:` | `1280px` | Desktops |
| `2xl:`| `1536px` | Desktops grandes |

**Ejemplo de uso:**

```html
<!-- Texto de 16px en mobile, 18px en tablet, 20px en desktop -->
<p class="k-text-base md:k-text-lg lg:k-text-xl">Texto responsive</p>

<!-- Oculto en mobile, visible como flex en desktop -->
<div class="k-hidden lg:k-flex">...</div>
```

### 2. Utilidad `.k-container`

Se ha añadido una clase `.k-container` para centrar y limitar el ancho del contenido. Es completamente responsive.

- **Mobile**: Ancho completo con `1rem` de padding.
- **Desktop**: El `max-width` se ajusta automáticamente a cada breakpoint.

```html
<div class="k-container">
  <!-- Tu contenido aquí -->
</div>
```

### 3. Utilidades de `max-width`

Controla el ancho máximo de tus elementos con las nuevas utilidades `k-max-w-*`.

**Ejemplos:**
- `k-max-w-md` -> `max-width: 28rem;`
- `k-max-w-full` -> `max-width: 100%;`
- `k-max-w-screen-lg` -> `max-width: 1024px;`

### 4. Utilidades de Efectos (`effects.py`)

Se ha añadido un módulo completo de efectos visuales:

- **Shadows**: `k-shadow`, `k-shadow-md`, `k-shadow-lg`, `k-shadow-xl`, etc.
- **Transitions**: `k-transition`, `k-transition-all`, `k-duration-*`, `k-ease-*`
- **Animations**: `k-animate-spin`, `k-animate-ping`, `k-animate-pulse`, `k-animate-bounce`
- **Opacity**: `k-opacity-0` a `k-opacity-100`
- **Blur**: `k-blur-sm`, `k-blur-md`, `k-backdrop-blur`

### 5. Utilidades de Layout Mejoradas

- **Gap**: `k-gap-*`, `k-gap-x-*`, `k-gap-y-*` para `flex` y `grid`.
- **Justify/Align**: Utilidades completas como `k-justify-evenly`, `k-items-stretch`, etc.
- **Grid**: `k-grid-rows-*`, `k-col-span-*`, `k-row-span-*`

### 6. Utilidades de Sizing Mejoradas

- **Fracciones**: `k-w-1/2`, `k-w-1/3`, `k-w-1/4`, etc.
- **Min/Max**: `k-min-w-*`, `k-min-h-*`, `k-max-h-*`

---

## 🔄 Cambios y Mejoras

### 1. Arquitectura del Compilador

- **`compiler.py`**: Ahora integra un generador de variantes responsive.
- **`responsive.py`**: Nuevo módulo que maneja toda la lógica de generación responsive. Esto hace el código más limpio y mantenible.
- **Módulos de utilidades**: Todos los módulos han sido refactorizados para ser compatibles con el nuevo sistema de generación.

### 2. Ejemplo HTML (`examples/index.html`)

- El archivo de ejemplo ha sido **completamente rediseñado** para ser una página de aterrizaje profesional y moderna.
- Demuestra el uso de **todas las nuevas características**, incluyendo el sistema responsive, container, shadows, transitions, y más.
- Ahora usa el archivo CSS local (`../dist/kardocss.css`) en lugar del CDN para facilitar el desarrollo.

### 3. Tamaño del Framework

Debido a la adición de miles de variantes responsive, el tamaño del archivo ha aumentado. Sin embargo, sigue siendo extremadamente ligero en comparación con otros frameworks.

| Versión | Tamaño Minificado | Gzipped (Estimado) |
|---|---|---|
| Anterior | 24.7 KB | ~5 KB |
| **Nueva** | **87.8 KB** | **~15 KB** |

Este tamaño es para el archivo completo. Para producción, se recomienda **implementar PurgeCSS** para eliminar todas las clases no utilizadas, reduciendo el tamaño final a solo unos pocos kilobytes.

---

## 📝 Guía de Actualización

Si estabas usando una versión anterior de KardoCSS, la actualización es sencilla ya que no hay cambios que rompan la compatibilidad.

1. **Reemplaza el archivo CSS**: Descarga la nueva versión de `kardocss.min.css` y reemplaza la antigua.

2. **Aprovecha las nuevas clases**: Revisa tu HTML y comienza a usar las nuevas variantes responsive y utilidades.

   **Antes:**
   ```html
   <div class="k-flex k-justify-between">
     <div class="k-w-1/2">Col 1</div>
     <div class="k-w-1/2">Col 2</div>
   </div>
   ```

   **Ahora (con responsive):**
   ```html
   <div class="k-container">
     <div class="k-grid k-grid-cols-1 md:k-grid-cols-2 k-gap-4">
       <div class="k-bg-white k-p-4 k-rounded-lg k-shadow">Col 1</div>
       <div class="k-bg-white k-p-4 k-rounded-lg k-shadow">Col 2</div>
     </div>
   </div>
   ```

3. **Usa `k-container`**: Envuelve tus secciones principales con `<div class="k-container">` para un layout centrado y con ancho limitado.

---

## Próximos Pasos

- **Dark Mode**: La próxima gran característica será la implementación de utilidades para modo oscuro (`dark:`).
- **PurgeCSS**: Se explorará la integración de PurgeCSS en el proceso de compilación para optimizar el tamaño en producción.

Gracias por usar KardoCSS. ¡Disfruta de las nuevas capacidades responsive!

