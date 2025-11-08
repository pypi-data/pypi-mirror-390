# Guía de Instalación y Uso de KardoCSS

Esta guía te ayudará a empezar a usar KardoCSS en tus proyectos.

## 📋 Tabla de Contenidos

1. [Instalación Rápida](#instalación-rápida)
2. [Uso con HTML Puro](#uso-con-html-puro)
3. [Uso con Python](#uso-con-python)
4. [Personalización](#personalización)
5. [Build desde Código Fuente](#build-desde-código-fuente)

---

## 🚀 Instalación Rápida

### Opción 1: CDN (Más Rápido)

Simplemente agrega esta línea en el `<head>` de tu HTML:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">
```

**¡Listo!** Ya puedes usar todas las clases de KardoCSS.

### Opción 2: Descarga Manual

1. Descarga el archivo CSS:
   - [kardocss.min.css](https://github.com/webcien/KardoCSS/raw/main/dist/kardocss.min.css) (24.7 KB)

2. Guárdalo en tu proyecto (ej: `css/kardocss.min.css`)

3. Inclúyelo en tu HTML:
```html
<link rel="stylesheet" href="css/kardocss.min.css">
```

### Opción 3: Python Package

Si usas Python y quieres personalizar el CSS:

```bash
pip install kardocss
```

---

## 🌐 Uso con HTML Puro

### Ejemplo Básico

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Sitio con KardoCSS</title>
    
    <!-- KardoCSS desde CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">
</head>
<body>
    <div class="k-container k-p-4">
        <h1 class="k-text-3xl k-font-bold k-text-primary">¡Hola Mundo!</h1>
        <p class="k-text-gray-700 k-mt-2">Este es un sitio con KardoCSS</p>
        <button class="k-btn k-btn-primary k-mt-4">Click aquí</button>
    </div>
</body>
</html>
```

### Ejemplo con Formulario

```html
<form class="k-p-4">
    <div class="k-mb-4">
        <label class="k-form-label">Nombre</label>
        <input type="text" class="k-input" placeholder="Tu nombre">
    </div>

    <div class="k-mb-4">
        <label class="k-form-label">Email</label>
        <input type="email" class="k-input" placeholder="tu@email.com">
    </div>

    <button type="submit" class="k-btn k-btn-primary">Enviar</button>
</form>
```

### Ejemplo con Layout

```html
<div class="k-flex k-justify-between k-items-center k-p-4">
    <div class="k-w-1/3 k-bg-primary k-text-white k-p-4 k-rounded">
        Columna 1
    </div>
    <div class="k-w-1/3 k-bg-secondary k-text-white k-p-4 k-rounded">
        Columna 2
    </div>
    <div class="k-w-1/3 k-bg-success k-text-white k-p-4 k-rounded">
        Columna 3
    </div>
</div>
```

---

## 🐍 Uso con Python

### Instalación

```bash
pip install kardocss
```

### Compilar CSS Básico

```python
from kardocss.compiler import KardoCSSCompiler

# Crear compilador
compiler = KardoCSSCompiler()

# Compilar CSS
css = compiler.compile()

# Guardar en archivo
with open('mi-estilo.css', 'w') as f:
    f.write(css)
```

### Compilar CSS Minificado

```python
from kardocss.compiler import KardoCSSCompiler

compiler = KardoCSSCompiler()

# Compilar y minificar
css_min = compiler.compile(minify=True)

# Guardar
with open('mi-estilo.min.css', 'w') as f:
    f.write(css_min)
```

---

## 🎨 Personalización

### Cambiar Colores

```python
from kardocss.core.config import KardoCSSConfig
from kardocss.compiler import KardoCSSCompiler

# Crear configuración personalizada
config = KardoCSSConfig()

# Cambiar color primario
config.set('colors.primary', '#ff6b6b')

# Cambiar color secundario
config.set('colors.secondary', '#4ecdc4')

# Compilar con configuración personalizada
compiler = KardoCSSCompiler(config)
css = compiler.compile()

# Guardar
with open('kardocss-custom.css', 'w') as f:
    f.write(css)
```

### Cambiar Prefijo

```python
from kardocss.core.config import KardoCSSConfig
from kardocss.compiler import KardoCSSCompiler

config = KardoCSSConfig()

# Cambiar prefijo de k- a mi-
config.set('prefix', 'mi-')

compiler = KardoCSSCompiler(config)
css = compiler.compile()

# Ahora las clases serán: mi-p-4, mi-text-xl, etc.
```

### Cambiar Espaciado

```python
from kardocss.core.config import KardoCSSConfig
from kardocss.compiler import KardoCSSCompiler

config = KardoCSSConfig()

# Agregar tamaño personalizado
config.set('spacing.72', '18rem')  # 288px

compiler = KardoCSSCompiler(config)
css = compiler.compile()

# Ahora puedes usar: k-p-72, k-m-72, etc.
```

---

## 🔨 Build desde Código Fuente

### Clonar Repositorio

```bash
git clone https://github.com/webcien/KardoCSS.git
cd KardoCSS
```

### Instalar Dependencias

```bash
pip install -e .
```

### Compilar CSS

```bash
python build.py
```

Esto generará:
- `dist/kardocss.css` (31.5 KB)
- `dist/kardocss.min.css` (24.7 KB)

### Usar CSS Compilado

```html
<!-- Desde archivo local -->
<link rel="stylesheet" href="dist/kardocss.min.css">
```

---

## 📦 Integración con Proyectos

### Con Flask (Python)

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

**templates/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">
</head>
<body>
    <div class="k-container k-p-4">
        <h1 class="k-text-3xl k-font-bold">Flask + KardoCSS</h1>
    </div>
</body>
</html>
```

### Con Django (Python)

**settings.py**:
```python
# No necesitas configurar nada, solo usa el CDN en tus templates
```

**templates/base.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

### Con FastAPI (Python)

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/webcien/KardoCSS@main/dist/kardocss.min.css">
    </head>
    <body>
        <div class="k-container k-p-4">
            <h1 class="k-text-3xl k-font-bold">FastAPI + KardoCSS</h1>
        </div>
    </body>
    </html>
    """
```

---

## 🎯 Casos de Uso

### Landing Page

```html
<body class="k-bg-gray-100">
    <header class="k-bg-primary k-text-white k-py-12">
        <div class="k-container k-text-center">
            <h1 class="k-text-4xl k-font-bold">Mi Producto</h1>
            <p class="k-text-xl k-mt-2">La mejor solución para tu negocio</p>
            <button class="k-btn k-btn-secondary k-mt-4">Comenzar</button>
        </div>
    </header>
    
    <section class="k-py-12">
        <div class="k-container">
            <div class="k-grid k-grid-cols-1 k-md:grid-cols-3 k-gap-6">
                <div class="k-bg-white k-p-6 k-rounded-lg k-shadow-md">
                    <h3 class="k-font-bold k-mb-2">Característica 1</h3>
                    <p class="k-text-gray-700">Descripción</p>
                </div>
                <!-- Más features... -->
            </div>
        </div>
    </section>
</body>
```

### Dashboard

```html
<div class="k-flex k-h-screen">
    <!-- Sidebar -->
    <aside class="k-w-64 k-bg-dark k-text-white k-p-4">
        <h2 class="k-text-xl k-font-bold k-mb-4">Dashboard</h2>
        <nav>
            <a href="#" class="k-block k-p-2 k-rounded k-mb-2">Inicio</a>
            <a href="#" class="k-block k-p-2 k-rounded k-mb-2">Usuarios</a>
            <a href="#" class="k-block k-p-2 k-rounded k-mb-2">Configuración</a>
        </nav>
    </aside>
    
    <!-- Main Content -->
    <main class="k-flex-1 k-p-6 k-bg-gray-100">
        <h1 class="k-text-3xl k-font-bold k-mb-6">Bienvenido</h1>
        
        <div class="k-grid k-grid-cols-1 k-md:grid-cols-3 k-gap-6">
            <div class="k-bg-white k-p-6 k-rounded-lg k-shadow-md">
                <h3 class="k-text-gray-500 k-mb-2">Usuarios</h3>
                <p class="k-text-3xl k-font-bold">1,234</p>
            </div>
            <!-- Más stats... -->
        </div>
    </main>
</div>
```

---

## ❓ Preguntas Frecuentes

### ¿Necesito Node.js?

**No.** KardoCSS está escrito en Python y genera CSS puro. Si solo quieres usar el CSS pre-compilado, no necesitas instalar nada.

### ¿Puedo usar KardoCSS con React/Vue/Angular?

**Sí.** Solo incluye el CSS desde CDN o descárgalo. Las clases funcionan con cualquier framework JavaScript.

### ¿Cómo actualizo a la última versión?

Si usas CDN, siempre tendrás la última versión. Si descargaste el archivo, vuelve a descargarlo desde GitHub.

### ¿Puedo usar KardoCSS en producción?

**Sí.** El CSS está minificado y optimizado para producción.

---

## 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/webcien/KardoCSS
- **PyPI**: https://pypi.org/project/kardocss/
- **Documentación**: [README.md](./README.md)
- **Ejemplos**: [examples/](./examples/)
- **Contribuir**: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 💡 Consejos

1. **Usa la versión minificada** (`kardocss.min.css`) en producción
2. **Usa la versión completa** (`kardocss.css`) en desarrollo para debugging
3. **Combina clases** para crear componentes personalizados
4. **Personaliza con Python** si necesitas cambiar colores o espaciado

---

**¡Disfruta usando KardoCSS!** 🎨

