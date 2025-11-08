# KardoCSS

**Framework CSS moderno, mobile-first y ultra-ligero con Dark Mode y PurgeCSS integrados**

KardoCSS es un framework CSS utility-first inspirado en Tailwind, pero diseñado para ser más ligero, modular y fácil de personalizar. Perfecto para proyectos que necesitan un CSS minimalista sin sacrificar funcionalidad.

## 🆕 Novedades en v1.1.1

- ✨ **Transiciones Mejoradas** - Nuevas utilidades: `k-transition-none`, `k-delay-*`, `k-ease-bounce`, `k-ease-back-*` ([Issue #1](https://github.com/webcien/KardoCSS/issues/1))
- 📦 **Disponible en Composer** - Ahora puedes instalar KardoCSS en proyectos PHP con `composer require webcien/kardocss`
- 📚 **Guía de Transiciones** - Documentación completa con 30+ ejemplos interactivos
- 🐛 **Corrección de Bugs** - Mejoras de estabilidad y rendimiento

### Novedades en v1.1.0

- 🌓 **Dark Mode Nativo** - Soporte completo para modo oscuro automático y manual
- 🧹 **PurgeCSS Integrado** - Tree-shaking automático que reduce el CSS hasta 90%
- ♿ **Accesibilidad Mejorada** - Soporte para `prefers-reduced-motion`
- 📚 **Documentación Expandida** - Guías completas de Dark Mode y PurgeCSS

## ✨ Características

- 🎯 **Utility-first** - Clases utilitarias con prefijo `k-`
- 🚀 **Responsive Completo** - Variantes responsive (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- 📱 **Mobile-first** - Diseño responsive desde el inicio
- ⚡ **Ultra-ligero** - 98.4 KB minificado completo, ~8-12 KB con PurgeCSS
- 🌓 **Dark Mode** - Modo oscuro automático y manual integrado
- 🧹 **PurgeCSS** - Tree-shaking automático para producción
- 🎨 **Personalizable** - Configuración flexible vía Python
- 🔧 **Modular** - Código Python organizado por utilidades
- 🚀 **Sin dependencias** - CSS puro generado desde Python
- 📦 **Pre-compilado** - Archivos CSS listos para usar
- 💻 **Múltiples formas de uso** - Pre-compilado, Composer (PHP), Python o CDN
- 🌐 **CDN disponible** - Usa desde jsDelivr sin instalación
- 📦 **Packagist** - Disponible en Composer para proyectos PHP

## 📦 Instalación

### Opción 1: Uso Directo (Recomendado para HTML/CSS)

#### Desde CDN (jsDelivr)

```html
<!-- Versión minificada (recomendado) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">

<!-- Versión completa (para desarrollo) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.css">
```

#### Descarga Manual

1. **Descarga el archivo CSS**:
   - [kardocss.min.css](https://github.com/webcien/KardoCSS/raw/main/dist/kardocss.min.css) - Producción
   - [kardocss.css](https://github.com/webcien/KardoCSS/raw/main/dist/kardocss.css) - Desarrollo

2. **Incluye en tu HTML**:
```html
<link rel="stylesheet" href="kardocss.min.css">
```

### Opción 2: Instalación con Composer (Para Proyectos PHP)

```bash
composer require webcien/kardocss
```

**Uso en PHP**:
```php
<?php
require_once __DIR__ . '/vendor/autoload.php';
use WebCien\KardoCSS\KardoCSS;
?>
<!DOCTYPE html>
<html>
<head>
    <?php echo KardoCSS::link(); ?>
</head>
<body>
    <!-- Tu contenido aquí -->
</body>
</html>
```

📚 **Guía completa**: [COMPOSER_GUIDE.md](./COMPOSER_GUIDE.md)

### Opción 3: Instalación con Python (Para Personalización)

```bash
# Desde PyPI
pip install kardocss

# O desde GitHub
git clone https://github.com/webcien/KardoCSS.git
cd KardoCSS
pip install -e .
```

## 🚀 Uso Rápido

### Uso Directo con HTML

Revisa el archivo `examples/index.html` para ver un ejemplo completo y profesional que demuestra todas las capacidades del framework.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Sitio con KardoCSS</title>
    
    <!-- Incluir KardoCSS desde archivo local -->
    <link rel="stylesheet" href="../dist/kardocss.css">
</head>
<body class="k-bg-gray-100">
    <!-- Header -->
    <header class="k-bg-primary k-text-white k-py-8 md:k-py-12">
        <div class="k-container k-text-center">
            <h1 class="k-text-3xl md:k-text-4xl k-font-bold">KardoCSS</h1>
            <p class="k-text-lg md:k-text-xl">Framework CSS Mobile-First</p>
        </div>
    </header>

    <!-- Contenido -->
    <section class="k-py-12">
        <div class="k-container">
            <div class="k-grid k-grid-cols-1 md:k-grid-cols-3 k-gap-6">
                <div class="k-bg-white k-p-6 k-rounded-lg k-shadow-md">
                    <h3 class="k-text-xl k-font-semibold k-mb-2">Feature 1</h3>
                    <p>Contenido de la tarjeta.</p>
                </div>
                <div class="k-bg-white k-p-6 k-rounded-lg k-shadow-md">
                    <h3 class="k-text-xl k-font-semibold k-mb-2">Feature 2</h3>
                    <p>Contenido de la tarjeta.</p>
                </div>
                <div class="k-bg-white k-p-6 k-rounded-lg k-shadow-md">
                    <h3 class="k-text-xl k-font-semibold k-mb-2">Feature 3</h3>
                    <p>Contenido de la tarjeta.</p>
                </div>
            </div>
        </div>
    </section>
</body>
</html>
```

### Compilar CSS con Python

```python
from kardocss.compiler import KardoCSSCompiler

compiler = KardoCSSCompiler()

# Compilar CSS completo
css = compiler.compile()

# Compilar y minificar
css_min = compiler.compile(minify=True)

# Guardar en archivo
with open('kardocss.min.css', 'w') as f:
    f.write(css_min)
```

## 📱 Sistema Responsive

KardoCSS es **mobile-first**. Las utilidades sin prefijo se aplican a todos los tamaños de pantalla, y puedes agregar prefijos de breakpoint para aplicar estilos en pantallas más grandes.

### Breakpoints

| Prefijo | Breakpoint | Descripción |
|---|---|---|
| `sm:` | `640px` | Teléfonos grandes / Tablets pequeñas |
| `md:` | `768px` | Tablets |
| `lg:` | `1024px` | Laptops |
| `xl:` | `1280px` | Desktops |
| `2xl:`| `1536px` | Desktops grandes |

### Ejemplo de Uso Responsive

```html
<!-- Apilado en mobile, 2 columnas en tablet, 4 en desktop -->
<div class="k-grid k-grid-cols-1 md:k-grid-cols-2 lg:k-grid-cols-4 k-gap-4">
    <!-- ... -->
</div>

<!-- Padding pequeño en mobile, más grande en desktop -->
<div class="k-p-4 md:k-p-8"></div>

<!-- Texto centrado en mobile, a la izquierda en desktop -->
<p class="k-text-center lg:k-text-left">Contenido</p>
```

## 🎨 Utilidades Disponibles

### Layout

- **Container**: `k-container`
- **Display**: `k-block`, `k-inline-block`, `k-flex`, `k-grid`, `k-hidden`
- **Position**: `k-static`, `k-relative`, `k-absolute`, `k-fixed`, `k-sticky`
- **Flexbox**: `k-flex-row`, `k-flex-col`, `k-flex-wrap`, `k-justify-*`, `k-items-*`
- **Grid**: `k-grid-cols-*`, `k-grid-rows-*`, `k-col-span-*`, `k-gap-*`
- **Overflow**: `k-overflow-auto`, `k-overflow-hidden`, `k-overflow-scroll`
- **Visibility**: `k-visible`, `k-invisible`

### Spacing

- **Padding**: `k-p-*`, `k-px-*`, `k-py-*`, `k-pt-*`, `k-pr-*`, `k-pb-*`, `k-pl-*`
- **Margin**: `k-m-*`, `k-mx-*`, `k-my-*`, `k-mt-*`, `k-mr-*`, `k-mb-*`, `k-ml-*`
- **Tamaños**: 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32

### Sizing

- **Width**: `k-w-*`, `k-w-full`, `k-w-screen`, `k-w-1/2`, `k-w-1/3`, etc.
- **Height**: `k-h-*`, `k-h-full`, `k-h-screen`
- **Max-Width**: `k-max-w-*`, `k-max-w-screen-*`
- **Min-Width**: `k-min-w-full`, `k-min-w-min`

### Colors

- **Text**: `k-text-{color}`
- **Background**: `k-bg-{color}`
- **Border**: `k-border-{color}`
- **Colores**: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `white`, `black`, `gray-100` a `gray-900`

### Typography

- **Font Size**: `k-text-xs`, `k-text-sm`, `k-text-base`, `k-text-lg` a `k-text-5xl`
- **Font Weight**: `k-font-thin`, `k-font-normal`, `k-font-bold`, `k-font-black`
- **Font Family**: `k-font-sans`, `k-font-serif`, `k-font-mono`
- **Text Align**: `k-text-left`, `k-text-center`, `k-text-right`, `k-text-justify`
- **Line Height**: `k-leading-none`, `k-leading-normal`, `k-leading-loose`

### Borders

- **Border Radius**: `k-rounded-sm`, `k-rounded`, `k-rounded-md`, `k-rounded-lg`, `k-rounded-full`
- **Border Width**: `k-border`, `k-border-2`, `k-border-4`, `k-border-8`
- **Border Style**: `k-border-solid`, `k-border-dashed`, `k-border-dotted`

### Transiciones y Animaciones

- **Transiciones**: `k-transition`, `k-transition-all`, `k-transition-colors`, `k-transition-opacity`, `k-transition-shadow`, `k-transition-transform`, `k-transition-none`
- **Duración**: `k-duration-75` a `k-duration-1000`
- **Easing**: `k-ease-linear`, `k-ease-in`, `k-ease-out`, `k-ease-in-out`, `k-ease-bounce`, `k-ease-back-in`, `k-ease-back-out`, `k-ease-back-in-out`
- **Delay**: `k-delay-75` a `k-delay-1000`
- **Animaciones**: `k-animate-spin`, `k-animate-ping`, `k-animate-pulse`, `k-animate-bounce`, `k-animate-fade-in`, `k-animate-slide-in-up`, `k-animate-slide-in-down`

📚 **Guía completa**: [TRANSITIONS_GUIDE.md](./TRANSITIONS_GUIDE.md)

### Otros Efectos

- **Box Shadow**: `k-shadow-sm`, `k-shadow`, `k-shadow-md`, `k-shadow-lg`, `k-shadow-xl`
- **Opacity**: `k-opacity-0`, `k-opacity-25`, `k-opacity-50`, `k-opacity-75`, `k-opacity-100`
- **Transitions**: `k-transition`, `k-transition-all`, `k-duration-*`, `k-ease-*`
- **Animations**: `k-animate-spin`, `k-animate-ping`, `k-animate-pulse`, `k-animate-bounce`

### Formularios Modernos

- `k-input`, `k-textarea`, `k-select`, `k-checkbox`, `k-radio`, `k-btn`, `k-btn-primary`, etc.

### Componentes

- **Badges**: `k-badge`, `k-badge-primary`, `k-badge-outline-*`
- **Gradientes**: `k-gradient-primary`, `k-gradient-sunset`, etc.

*Todas las utilidades principales tienen variantes responsive y soporte para dark mode.*

### Dark Mode

- **Backgrounds**: `dark:k-bg-primary`, `dark:k-bg-gray-900`, etc.
- **Text**: `dark:k-text-white`, `dark:k-text-gray-100`, etc.
- **Borders**: `dark:k-border-gray-700`, etc.
- **Modo automático**: Respeta `prefers-color-scheme`
- **Modo manual**: Toggle con clase `.dark` en `<html>`

**Ejemplo**:
```html
<div class="k-bg-white dark:k-bg-gray-900 k-text-gray-900 dark:k-text-white">
  Contenido que se adapta automáticamente
</div>
```

📚 **Guía completa**: [DARK_MODE_GUIDE.md](./DARK_MODE_GUIDE.md)

### PurgeCSS

Reduce el tamaño del CSS en producción eliminando clases no utilizadas:

```python
from kardocss.compiler import KardoCSSCompiler

compiler = KardoCSSCompiler()
css = compiler.compile(
    minify=True,
    purge=['**/*.html', '**/*.jsx']
)
```

**Resultado**: 98.4 KB → ~8-12 KB (reducción de 80-90%)

📚 **Guía completa**: [PURGE_GUIDE.md](./PURGE_GUIDE.md)

## 📊 Tamaño del Framework

| Versión | Tamaño | Gzipped (Estimado) | Con PurgeCSS |
|---|---|---|---|
| `kardocss.css` | 120.9 KB | ~22 KB | N/A |
| `kardocss.min.css` | 98.4 KB | ~17 KB | ~8-12 KB |

## 🗺️ Roadmap

- [x] Utilidades básicas (spacing, colors, typography)
- [x] Sistema de layout (flex, grid)
- [x] Borders y sizing
- [x] Formularios modernos
- [x] Sistema de badges y gradientes
- [x] Archivos CSS pre-compilados y CDN
- [x] **Sistema responsive completo**
- [x] **Utilidades de efectos (shadows, transitions, animations)**
- [x] **Clase `k-container` responsive**
- [x] **Utilidades de `max-width`**
- [x] **Dark mode nativo** (v1.1.0)
- [x] **PurgeCSS integrado** (v1.1.0)
- [x] **Soporte para `prefers-reduced-motion`** (v1.1.0)
- [ ] CLI mejorado para compilación
- [ ] Container queries
- [ ] Aspect ratio utilities
- [ ] Plugin para PostCSS
- [ ] Más animaciones y transiciones

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor lee [CONTRIBUTING.md](./CONTRIBUTING.md) para detalles.

## 📄 Licencia

MIT License - ver [LICENSE](./LICENSE) para detalles.

---

**KardoCSS** - Framework CSS moderno y ultra-ligero 🎨

