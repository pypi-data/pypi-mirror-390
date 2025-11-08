# KardoCSS

<p align="center">
  <img src="https://raw.githubusercontent.com/webcien/KardoCSS/main/assets/KardoCSS.png" alt="KardoCSS Logo" width="400">
</p>

**Modern, mobile-first, and ultra-lightweight CSS framework with built-in Dark Mode and PurgeCSS.**

KardoCSS is a utility-first CSS framework inspired by Tailwind, but designed to be lighter, more modular, and easier to customize. Perfect for projects that need a minimalist CSS without sacrificing functionality.

---

## 🌍 Translations

- [Español](./docs/es/README.es.md)

---

## 🆕 What's New in v1.1.3

- ✨ **npm Support** - KardoCSS is now available on npm!
- 🇬🇧 **English Documentation** - All documentation is now primarily in English.
- ✨ **Enhanced Transitions** - New utilities: `k-transition-none`, `k-delay-*`, `k-ease-bounce`, `k-ease-back-*` (from [Issue #1](https://github.com/webcien/KardoCSS/issues/1))
- 📦 **Composer Support** - Install KardoCSS in PHP projects with `composer require webcien/kardocss`

---

## ✨ Features

- 🎯 **Utility-First** - Utility classes with a `k-` prefix
- 🚀 **Fully Responsive** - Responsive variants (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- 📱 **Mobile-First** - Responsive design from the ground up
- ⚡ **Ultra-Lightweight** - 99.0 KB minified, ~8-12 KB with PurgeCSS
- 🌓 **Dark Mode** - Built-in automatic and manual dark mode
- 🧹 **PurgeCSS** - Automatic tree-shaking for production
- 🎨 **Customizable** - Flexible configuration via Python
- 🔧 **Modular** - Python code organized by utilities
- 🚀 **No Dependencies** - Pure CSS generated from Python
- 📦 **Pre-compiled** - Ready-to-use CSS files
- 💻 **Multiple Installation Methods** - npm, Composer, PyPI, CDN, or direct download
- 🌐 **CDN Available** - Use from jsDelivr without installation

---

## 📦 Installation

### Option 1: npm (Recommended for JS Projects)

```bash
npm install kardocss
```

**Usage in your project:**
```javascript
// main.js or index.js
import 'kardocss/dist/kardocss.min.css';
```

📚 **Full Guide**: [NPM_GUIDE.md](./NPM_GUIDE.md)

### Option 2: Composer (For PHP Projects)

```bash
composer require webcien/kardocss
```

**Usage in PHP:**
```php
<?php
require_once __DIR__ . '/vendor/autoload.php';
use WebCien\KardoCSS\KardoCSS;
?>
<head>
    <?php echo KardoCSS::link(); ?>
</head>
```

📚 **Full Guide**: [COMPOSER_GUIDE.md](./COMPOSER_GUIDE.md)

### Option 3: CDN (For HTML/CSS)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/kardocss@latest/dist/kardocss.min.css">
```

### Option 4: PyPI (For Python Customization)

```bash
pip install kardocss
```

---

## 🚀 Quick Start

Check out the `examples/index.html` file for a complete, professional example that demonstrates the framework's capabilities.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Site with KardoCSS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/kardocss@latest/dist/kardocss.min.css">
</head>
<body class="k-bg-gray-100 dark:k-bg-gray-900">
    <!-- Header -->
    <header class="k-bg-primary k-text-white k-py-8">
        <div class="k-container k-text-center">
            <h1 class="k-text-4xl k-font-bold">KardoCSS</h1>
            <p class="k-text-xl">Modern CSS Framework</p>
        </div>
    </header>

    <!-- Content -->
    <section class="k-py-12">
        <div class="k-container">
            <div class="k-grid k-grid-cols-1 md:k-grid-cols-3 k-gap-6">
                <div class="k-bg-white dark:k-bg-gray-800 k-p-6 k-rounded-lg k-shadow-md">
                    <h3 class="k-text-xl k-font-semibold k-mb-2 dark:k-text-white">Feature 1</h3>
                    <p class="k-text-gray-600 dark:k-text-gray-300">Card content.</p>
                </div>
                <!-- More cards... -->
            </div>
        </div>
    </section>
</body>
</html>
```

---

## 🎨 Available Utilities

KardoCSS includes a wide range of utilities for layout, spacing, colors, typography, and more.

- **Layout**: Container, Display, Position, Flexbox, Grid
- **Spacing**: Padding, Margin
- **Sizing**: Width, Height, Max-Width, Min-Width
- **Colors**: Text, Background, Border (with a default palette)
- **Typography**: Font Size, Weight, Family, Text Align, Line Height
- **Borders**: Radius, Width, Style
- **Transitions & Animations**: Transition, Duration, Easing, Delay, Animations
- **Effects**: Box Shadow, Opacity
- **Forms**: Modern styles for inputs, buttons, selects, etc.
- **Components**: Badges, Gradients

*All major utilities are responsive and support dark mode.*

---

## 🗺️ Roadmap

- [x] Core utilities (spacing, colors, typography)
- [x] Layout system (flex, grid)
- [x] Responsive system
- [x] Dark mode
- [x] PurgeCSS integration
- [x] Composer support
- [x] **npm support**
- [ ] Improved CLI
- [ ] Container queries
- [ ] Aspect ratio utilities
- [ ] PostCSS plugin

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

