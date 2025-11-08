# Changelog

Todos los cambios notables en KardoCSS serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1.1] - 2025-11-07

### ✨ Características Nuevas (Issue #1)

En respuesta al [Issue #1](https://github.com/webcien/KardoCSS/issues/1) de la comunidad, se han agregado utilidades de transición faltantes:

- ✨ **`k-transition-none`** - Deshabilita todas las transiciones
- ✨ **`k-delay-*`** - Retardos de transición (75ms, 100ms, 150ms, 200ms, 300ms, 500ms, 700ms, 1000ms)
- ✨ **`k-ease-bounce`** - Función de easing con efecto bounce
- ✨ **`k-ease-back-in`** - Función de easing back-in
- ✨ **`k-ease-back-out`** - Función de easing back-out
- ✨ **`k-ease-back-in-out`** - Función de easing back-in-out

### 📚 Documentación

- ✨ **`TRANSITIONS_GUIDE.md`** - Guía completa de transiciones y animaciones
- ✨ **`examples/transitions-demo.html`** - Demo interactivo con 30+ ejemplos
- 📖 README actualizado con sección de transiciones

### 📊 Métricas

- **Tamaño**: 121.6 KB (sin minificar), 99.0 KB (minificado)
- **Clases nuevas**: 13 (1 transition-none + 8 delays + 4 easings)
- **Incremento**: +0.6 KB vs v1.1.0

### 🚀 Agradecimientos

Gracias a [@screwtape151](https://github.com/screwtape151) por reportar el Issue #1 y sugerir estas mejoras.

---

## [1.1.0] - 2025-10-26

### 🎉 Características Nuevas

#### Dark Mode Nativo
- ✨ Soporte completo para modo oscuro automático usando `prefers-color-scheme`
- ✨ Toggle manual de dark mode con clase `.dark` en `<html>`
- ✨ Utilidades `dark:` para backgrounds, texto y bordes
- ✨ Paleta de colores optimizada para modo oscuro
- ✨ Variables CSS personalizadas para dark mode
- ✨ Persistencia de preferencia en localStorage
- ✨ Transiciones suaves entre temas
- 📚 Guía completa: `DARK_MODE_GUIDE.md`
- 🎨 Demo interactiva: `examples/dark-mode-demo.html`

#### PurgeCSS / Tree-Shaking
- ✨ Sistema integrado de purging para eliminar CSS no utilizado
- ✨ Reducción de 80-90% en tamaño de producción (98.4 KB → ~8-12 KB)
- ✨ Escaneo automático de archivos HTML/JSX/Vue/etc.
- ✨ Safelist configurable para clases dinámicas
- ✨ API simple de Python para integración en build tools
- ✨ Estadísticas detalladas del proceso de purging
- 📚 Guía completa: `PURGE_GUIDE.md`

#### Accesibilidad
- ♿ Soporte para `prefers-reduced-motion`
- ♿ Deshabilita animaciones automáticamente para usuarios sensibles al movimiento
- ♿ Cumplimiento WCAG 2.1 Nivel AA en ambos modos (light/dark)

### 📝 Mejoras

- 📖 Documentación expandida con guías detalladas
- 📖 Ejemplos actualizados con dark mode
- 📖 README mejorado con información de v1.1.0
- 🎨 Mejor organización de módulos
- 🔧 Refactorización del compilador para mejor extensibilidad

### 📊 Métricas

- **Tamaño completo**: 120.9 KB (sin minificar), 98.4 KB (minificado)
- **Tamaño con PurgeCSS**: ~8-12 KB (típico en producción)
- **Clases totales**: ~3500+ (incluyendo variantes dark mode)
- **Overhead de dark mode**: +12.5 KB (~13%)

### 🚀 Migración desde v1.0.0

Si usas KardoCSS desde CDN o archivos pre-compilados, no necesitas cambiar nada. El dark mode está incluido automáticamente.

Para habilitar dark mode, agrega clases `dark:` a tus elementos:
```html
<div class="k-bg-white dark:k-bg-gray-900">
  Contenido
</div>
```

Para usar PurgeCSS en compilación Python:
```python
css = compiler.compile(minify=True, purge=['**/*.html'])
```

---

## [1.0.0] - 2025-10-26

### 🎉 Primera Versión Estable

- ✨ Sistema responsive completo (sm, md, lg, xl, 2xl)
- ✨ Clase `k-container` responsive
- ✨ Utilidades de `max-width`, `gap`, `shadow`
- ✨ Efectos completos (transitions, animations, opacity)
- 🏭 Módulo `responsive.py` para generación de variantes
- 📖 Documentación completa
- 📦 Disponible en PyPI y jsDelivr CDN

**Métricas**: 87.8 KB minificado, ~3000+ clases

---

## [0.1.0-alpha] - 2024-10-21

### Agregado

#### Utilidades de Formularios Modernos (50+ clases)
- **Inputs y Textareas**: Estilos modernos con estados de focus, disabled y error
  - `.k-input` - Input base con bordes redondeados y transiciones suaves
  - `.k-textarea` - Textarea con auto-resize opcional
  - Estados de focus con ring azul sutil
  - Estados disabled con opacidad reducida
  - Placeholders estilizados

- **Selects**: Select estilizado con flecha personalizada
  - `.k-select` - Select moderno con icono de flecha
  - Consistente con el diseño de inputs

- **Checkboxes y Radio Buttons**: Controles personalizados
  - `.k-checkbox` - Checkbox personalizado con checkmark animado
  - `.k-radio` - Radio button con círculo interior
  - Estados checked con colores primarios
  - Transiciones suaves en todos los estados

- **Toggle Switch**: Interruptor moderno tipo iOS
  - `.k-switch` - Toggle switch animado
  - Estados on/off con transiciones
  - Diseño moderno y accesible

- **Grupos de Inputs**: Inputs con iconos y addons
  - `.k-input-group` - Contenedor para inputs con iconos
  - `.k-input-icon` - Input con icono integrado
  - `.k-input-addon` - Addons para inputs (prefijos/sufijos)

- **Labels y Mensajes**: Elementos de formulario complementarios
  - `.k-form-label` - Label estilizado para formularios
  - `.k-form-error` - Mensaje de error en rojo
  - `.k-form-help` - Texto de ayuda en gris
  - `.k-form-success` - Mensaje de éxito en verde

- **Estados Especiales**: Indicadores visuales
  - `.k-input-loading` - Spinner de carga para inputs
  - `.k-input-error` - Estado de error con borde rojo
  - `.k-input-success` - Estado de éxito con borde verde

#### Sistema de Badges (16+ variantes)
- **Badges Sólidos**: 8 variantes de color
  - `.k-badge-primary` - Badge azul
  - `.k-badge-secondary` - Badge gris
  - `.k-badge-success` - Badge verde
  - `.k-badge-danger` - Badge rojo
  - `.k-badge-warning` - Badge amarillo
  - `.k-badge-info` - Badge cyan
  - `.k-badge-light` - Badge claro
  - `.k-badge-dark` - Badge oscuro

- **Badges con Borde**: 8 variantes outline
  - `.k-badge-outline-{color}` - Badge con borde y fondo transparente
  - Todas las variantes de color disponibles
  - Perfecto para estados secundarios

- **Características**:
  - Tamaño consistente y legible
  - Padding y border-radius optimizados
  - Transiciones suaves en hover
  - Tipografía clara y accesible

#### Sistema de Gradientes (12 gradientes predefinidos)
- **Gradientes Principales**:
  - `.k-gradient-primary` - Azul a índigo (profesional)
  - `.k-gradient-sunset` - Naranja a rosa (cálido)
  - `.k-gradient-ocean` - Azul a verde (fresco)
  - `.k-gradient-fire` - Rojo a naranja (energético)
  - `.k-gradient-purple` - Púrpura a rosa (elegante)
  - `.k-gradient-green` - Verde a cyan (natural)

- **Gradientes Temáticos**:
  - `.k-gradient-warm` - Amarillo a rojo (cálido)
  - `.k-gradient-cool` - Azul a púrpura (frío)
  - `.k-gradient-night` - Oscuro a azul (nocturno)
  - `.k-gradient-dawn` - Rosa a amarillo (amanecer)
  - `.k-gradient-forest` - Verde oscuro a claro (naturaleza)
  - `.k-gradient-sky` - Azul claro a blanco (cielo)

- **Características**:
  - Gradientes lineales de 135 grados
  - Colores armoniosos y profesionales
  - Listos para usar en backgrounds
  - Combinables con otras utilidades

### Modificado
- **Compiler**: Actualizado para manejar tipos mixtos de utilidades (listas y strings)
  - Soporte para funciones que retornan strings completos
  - Mejor manejo de utilidades complejas
  - Optimización del proceso de compilación

- **README.md**: Documentación completa actualizada
  - Ejemplos de uso de todas las nuevas utilidades
  - Tabla de tamaños del framework
  - Guías de uso para formularios, badges y gradientes
  - Roadmap actualizado

- **CSS Compilado**: Recompilado con todas las nuevas utilidades
  - kardocss.css: 32,276 caracteres (32 KB)
  - kardocss.min.css: 25,295 caracteres (24.7 KB)
  - Reducción del 21.6% con minificación
  - Estimado ~5 KB gzipped

### Rendimiento
- **Tamaño total**: 24.7 KB minificado (sin gzip)
- **Estimado gzipped**: ~5 KB
- **Utilidades totales**: 200+ clases disponibles
- **Sin dependencias**: CSS puro generado desde Python

### Notas de Actualización
- Todas las nuevas utilidades usan el prefijo `k-` estándar
- Compatible con versiones anteriores
- No se requieren cambios en código existente
- Las nuevas utilidades son completamente opcionales

### Roadmap para v0.2.0
- [ ] Animaciones y transiciones predefinidas
- [ ] Sistema de shadows y effects
- [ ] Grid system avanzado con 12 columnas
- [ ] Dark mode utilities
- [ ] Purge CSS automático para optimización
- [ ] CLI para compilación y watch mode
- [ ] Plugin para PostCSS
- [ ] Más variantes responsive

---

## [0.0.1-alpha] - 2024-10-20

### Agregado
- Versión inicial de KardoCSS
- Utilidades básicas (spacing, colors, typography)
- Sistema de layout (flex, grid)
- Borders y sizing
- Configuración personalizable
- Compilador Python

[0.1.0-alpha]: https://github.com/webcien/KardoCSS/compare/v0.0.1-alpha...v0.1.0-alpha
[0.0.1-alpha]: https://github.com/webcien/KardoCSS/releases/tag/v0.0.1-alpha

