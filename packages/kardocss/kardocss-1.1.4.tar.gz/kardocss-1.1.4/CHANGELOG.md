# Changelog

All notable changes to KardoCSS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.4] - 2025-11-07

### 🐛 Bug Fixes

- **Transform utilities**: Fixed scale, rotate, and translate classes to apply transform directly instead of just setting CSS variables
- **Gradient utilities**: Added missing predefined gradient classes (primary, sunset, ocean, fire, purple, green, warm, cool)
- **Examples**: Fixed transitions-demo.html and index.html to work correctly

### ✨ Enhancements

- **dark-mode-demo.html**: Made header sticky for better navigation
- **All examples**: Added KardoCSS logo to all example pages

### 📦 Package Updates

- Version bumped to 1.1.4 across all package managers
- CSS size: 101.0 KB minified

---

## [1.1.3] - 2025-11-07

### ✨ New Features

- **npm Support**: KardoCSS is now available on npm! Install with `npm install kardocss`.
- **English Documentation**: All documentation is now primarily in English.

### 📚 Documentation

- **NPM_GUIDE.md**: Complete guide for npm installation and usage.
- **README.md**: Updated with npm installation instructions.

---

## [1.1.3] - 2025-11-07

### ✨ New Features

- **npm Support**: KardoCSS is now available on npm! Install with `npm install kardocss`.
- **English Documentation**: All documentation is now primarily in English.
- **Spanish Documentation**: Spanish documentation moved to `docs/es/` directory.
- **Logo**: Official KardoCSS logo added to `assets/` directory.

### 📚 Documentation

- **NPM_GUIDE.md**: Complete guide for npm installation and usage with React, Vue, Vite, Next.js, Nuxt, and Astro.
- **README.md**: Now in English with npm installation instructions.
- **CONTRIBUTING.md**: Updated to English.
- **All Guides**: Translated to English (CHANGELOG, COMPOSER_GUIDE, TRANSITIONS_GUIDE, DARK_MODE_GUIDE, PURGE_GUIDE).

### 📦 Package Managers

- **npm**: `npm install kardocss`
- **Composer**: `composer require webcien/kardocss`
- **PyPI**: `pip install kardocss`
- **CDN**: `https://cdn.jsdelivr.net/npm/kardocss@latest/dist/kardocss.min.css`

---

## [1.1.2] - 2025-11-07

### ✨ New Features

- **Composer/Packagist Support**: KardoCSS is now available on Packagist.
- **PHP Class**: `WebCien\KardoCSS\KardoCSS` for integration with PHP projects.
- **composer.json**: Full configuration for Packagist.
- **PHP Example**: `examples/php-example.php` with full usage.

### 📚 Documentation

- **COMPOSER_GUIDE.md**: Complete guide for Composer installation and usage.
- **README.md**: Updated with Composer installation section.

---

## [1.1.1] - 2025-11-07

### ✨ New Features (Issue #1)

In response to community [Issue #1](https://github.com/webcien/KardoCSS/issues/1), missing transition utilities have been added:

- `k-transition-none`: Disables all transitions.
- `k-delay-*`: Transition delays (75ms to 1000ms).
- `k-ease-bounce`, `k-ease-back-*`: New easing functions.

### 📚 Documentation

- **TRANSITIONS_GUIDE.md**: Complete guide for transitions and animations.
- **examples/transitions-demo.html**: Interactive demo with 30+ examples.

### 🙏 Acknowledgements

Thanks to [@screwtape151](https://github.com/screwtape151) for reporting Issue #1 and suggesting these improvements.

---

## [1.1.0] - 2025-10-26

### 🎉 New Features

- **Native Dark Mode**: Full support for automatic and manual dark mode.
- **Integrated PurgeCSS**: Automatic tree-shaking to reduce CSS size by 80-90%.
- **Accessibility**: Support for `prefers-reduced-motion`.

### 📚 Documentation

- **DARK_MODE_GUIDE.md**: Complete guide for dark mode.
- **PURGE_GUIDE.md**: Complete guide for PurgeCSS.

---

## [1.0.0] - 2025-10-26

### 🎉 First Stable Release

- **Responsive System**: Full responsive system with breakpoints.
- **Container Class**: Responsive `k-container` class.
- **New Utilities**: `max-width`, `gap`, `shadow`.
- **Effects**: Full transitions, animations, and opacity utilities.

---

## [0.1.0-alpha] - 2024-10-21

### Added

- **Modern Forms**: 50+ classes for inputs, selects, checkboxes, etc.
- **Badges**: 16+ variants for solid and outline badges.
- **Gradients**: 12 predefined gradients.

---

## [0.0.1-alpha] - 2024-10-20

### Added

- Initial version of KardoCSS.
- Core utilities (spacing, colors, typography).
- Layout system (flex, grid).
- Borders and sizing.
- Customizable configuration.
- Python compiler.

