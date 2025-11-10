# Changelog

All notable changes to KardoCSS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2025-11-09

### ✨ New Features

- **Optional Modules System**: Modular architecture for advanced features
  - `modules.container_queries` (enabled by default)
  - `modules.tv_breakpoints` (prepared for v1.3.0)
  - `modules.fluid_typography` (planned for v1.4.0)
  - `modules.aspect_ratio` (planned for v1.4.0)
  - Compiler respects module flags before generating utilities
  - Config system supports nested module configuration
- **Container Queries Module**: Now optional, enabled by default
  - New utility classes: `k-cq-{breakpoint}:{utility}`
  - 4 breakpoints: sm (320px), md (640px), lg (960px), xl (1280px)
  - Support for display, flex, grid, text, padding, and gap utilities
  - Named containers: `k-container-card`, `k-container-sidebar`, `k-container-main`
  - Container types: `k-container-inline-size`, `k-container-size`, `k-container-normal`
- **CI/CD Size Check**: GitHub Actions workflow to enforce CSS size limits
  - Automatic size verification on push and pull requests
  - Limits: 130 KB (unminified), 110 KB (minified)
  - Detailed size reports in job summaries
  - Fails build if size limits are exceeded
- **Build & Test Workflow**: Multi-version Python testing (3.10, 3.11, 3.12)
  - Automatic CSS compilation verification
  - Content validation (checks for expected classes)
  - Artifact uploads for debugging
- **KardoTV Preparation**: Structure ready for TV breakpoints module (v1.3.0)
  - `tv_config` in config.py with wide (1600px) and tv (2400px) breakpoints
  - Placeholder module `tv_breakpoints.py`
  - Complete roadmap document

### 📚 Documentation

- **OPTIONAL_MODULES_GUIDE.md**: Complete guide for optional modules system (English)
- **OPTIONAL_MODULES_GUIDE.es.md**: Optional modules guide (Spanish)
- **CONTAINER_QUERIES_GUIDE.md**: Complete guide for container queries (English)
- **SIZE_CHECK_GUIDE.md**: Complete guide for CI/CD size checks (English)
- **KARDOTV_ROADMAP.md**: Detailed roadmap for KardoTV module (v1.3.0)
- **docs/es/CONTAINER_QUERIES_GUIDE.es.md**: Container queries guide (Spanish)
- **docs/es/SIZE_CHECK_GUIDE.es.md**: Size check guide (Spanish)
- **examples/container-queries-demo.html**: Interactive demo with 4 examples
- **README.md**: Updated with v1.2.0 features and optional modules

### 🔄 Changed

- Updated size limit from 100 KB to 110 KB (minified) to accommodate Container Queries
- Optimized Container Queries module to minimize CSS size impact (+5.1 KB)
- CSS size: 105.1 KB minified (from 99.0 KB)

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

