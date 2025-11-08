"""
Compilador de KardoCSS

Genera CSS a partir de la configuración y las utilidades definidas.
Optimizado para rendimiento y tamaño de archivo.
"""

from typing import List, Dict, Any
from kardocss.core.config import KardoCSSConfig
from kardocss.utilities.spacing import generate_spacing_utilities
from kardocss.utilities.colors import generate_color_utilities
from kardocss.utilities.typography import generate_typography_utilities
from kardocss.utilities.layout import generate_layout_utilities
from kardocss.utilities.borders import generate_border_utilities
from kardocss.utilities.sizing import generate_sizing_utilities
from kardocss.utilities.forms import generate_form_utilities
from kardocss.utilities.badges import generate_badge_utilities
from kardocss.utilities.gradients import generate_gradient_utilities
from kardocss.utilities.effects import generate_effect_utilities
from kardocss.utilities.dark_mode import generate as generate_dark_mode
from kardocss.compiler.responsive import ResponsiveGenerator


class KardoCSSCompiler:
    """
    Compilador principal de KardoCSS.
    
    Genera CSS completo a partir de la configuración y las utilidades.
    Soporta minificación, purging y optimización.
    """
    
    def __init__(self, config: KardoCSSConfig = None):
        """
        Inicializa el compilador.
        
        Args:
            config: Configuración de KardoCSS (usa default si no se proporciona)
        """
        self.config = config or KardoCSSConfig()
        self.utilities: List[str] = []
        self.base_styles: List[str] = []
    
    def compile(self, minify: bool = False, purge: List[str] = None) -> str:
        """
        Compila el CSS completo.
        
        Args:
            minify: Si debe minificar el CSS
            purge: Lista de archivos HTML/templates para purging (opcional)
        
        Returns:
            CSS compilado como string
        """
        # Generar estilos base
        self._generate_base_styles()
        
        # Generar utilidades
        self._generate_utilities()
        
        # Combinar todo
        css = self._combine_styles()
        
        # Purge si se especificó
        if purge:
            css = self._purge_unused(css, purge)
        
        # Minificar si se especificó
        if minify:
            css = self._minify(css)
        
        return css
    
    def _generate_base_styles(self) -> None:
        """Genera estilos base (reset, normalize, etc.)."""
        self.base_styles = [
            "/* KardoCSS - Framework CSS Mobile-First */",
            "/* Version: 1.1.3 - npm Support & English Documentation */",
            "",
            "/* Base Styles */",
            "*, *::before, *::after {",
            "  box-sizing: border-box;",
            "  margin: 0;",
            "  padding: 0;",
            "}",
            "",
            "html {",
            "  font-size: 16px;",
            "  -webkit-text-size-adjust: 100%;",
            "}",
            "",
            "body {",
            f"  font-family: {self.config.get('typography.families.sans')};",
            "  line-height: 1.5;",
            "  color: #212529;",
            "  background-color: #ffffff;",
            "}",
            "",
            "img, picture, video, canvas, svg {",
            "  display: block;",
            "  max-width: 100%;",
            "}",
            "",
            "input, button, textarea, select {",
            "  font: inherit;",
            "}",
            "",
        ]
    
    def _generate_utilities(self) -> None:
        """Genera todas las utilidades CSS."""
        prefix = self.config.get("prefix", "k-")
        
        # Generar utilidades de cada categoría
        utilities = []
        
        # Spacing (margin, padding)
        utilities.extend(generate_spacing_utilities(self.config, prefix))
        
        # Colors (background, text, border)
        utilities.extend(generate_color_utilities(self.config, prefix))
        
        # Typography (font-size, weight, family)
        utilities.extend(generate_typography_utilities(self.config, prefix))
        
        # Layout (display, flex, grid)
        utilities.extend(generate_layout_utilities(self.config, prefix))
        
        # Borders (radius, width, style)
        utilities.extend(generate_border_utilities(self.config, prefix))
        
        # Sizing (width, height)
        utilities.extend(generate_sizing_utilities(self.config, prefix))
        
        # Forms (inputs, buttons, etc.)
        utilities.append(generate_form_utilities())
        
        # Badges
        utilities.append(generate_badge_utilities(self.config))
        
        # Gradients
        utilities.append(generate_gradient_utilities(self.config))
        
        # Effects (shadows, opacity, transitions, animations)
        utilities.extend(generate_effect_utilities(self.config, prefix))
        
        # Dark Mode
        utilities.append(generate_dark_mode())
        
        self.utilities = utilities
    
    def _combine_styles(self) -> str:
        """Combina estilos base y utilidades."""
        all_styles = []
        
        # Agregar base styles
        all_styles.extend(self.base_styles)
        
        # Agregar separador
        all_styles.append("")
        all_styles.append("/* Utilities */")
        all_styles.append("")
        
        # Agregar utilidades
        all_styles.extend(self.utilities)
        
        # Generar responsive variants
        all_styles.append("")
        all_styles.append("/* Responsive Variants */")
        all_styles.append("")
        all_styles.extend(self._generate_responsive_variants())
        
        return "\n".join(all_styles)
    
    def _generate_responsive_variants(self) -> List[str]:
        """Genera variantes responsive de las utilidades."""
        prefix = self.config.get("prefix", "k-")
        
        # Crear generador responsive
        generator = ResponsiveGenerator(self.config, prefix)
        
        # Generar variantes responsive de todas las utilidades
        variants = generator.generate_responsive_variants(self.utilities)
        
        # Agregar variantes específicas del container
        variants.extend(self._generate_container_responsive())
        
        return variants
    
    def _generate_container_responsive(self) -> List[str]:
        """Genera media queries específicas para el container."""
        variants = []
        prefix = self.config.get("prefix", "k-")
        breakpoints = self.config.get("breakpoints", {})
        container_config = self.config.get("container", {})
        max_widths = container_config.get("maxWidth", {})
        
        for bp_name, bp_value in breakpoints.items():
            if bp_name in max_widths:
                max_width = max_widths[bp_name]
                variants.append(f"@media (min-width: {bp_value}) {{")
                variants.append(f"  .{prefix}container {{ max-width: {max_width}; }}")
                variants.append("}")
        
        return variants
    
    def _purge_unused(self, css: str, files: List[str]) -> str:
        """
        Elimina clases CSS no utilizadas.
        
        Args:
            css: CSS completo
            files: Lista de archivos para escanear (glob patterns)
        
        Returns:
            CSS purgado
        """
        from kardocss.compiler.purge import CSSPurger
        
        purger = CSSPurger(css)
        purger.scan_files(files)
        
        # Safelist: clases que siempre deben mantenerse
        safelist = [
            'k-container',
            'k-btn',
            'k-input',
            'k-select',
            'k-textarea',
            'k-checkbox',
            'k-radio',
            'k-form-label',
            'k-badge',
        ]
        purger.add_safelist(safelist)
        
        return purger.purge(keep_base_styles=True)
    
    def _minify(self, css: str) -> str:
        """
        Minifica el CSS.
        
        Args:
            css: CSS a minificar
        
        Returns:
            CSS minificado
        """
        # Eliminar comentarios
        import re
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Eliminar espacios en blanco innecesarios
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*{\s*', '{', css)
        css = re.sub(r'\s*}\s*', '}', css)
        css = re.sub(r'\s*:\s*', ':', css)
        css = re.sub(r'\s*;\s*', ';', css)
        css = re.sub(r';\s*}', '}', css)
        
        return css.strip()
    
    def compile_to_file(self, output_path: str, minify: bool = False) -> None:
        """
        Compila y guarda el CSS en un archivo.
        
        Args:
            output_path: Path del archivo de salida
            minify: Si debe minificar el CSS
        """
        css = self.compile(minify=minify)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css)
        
        print(f"✅ CSS compilado: {output_path}")
        print(f"📦 Tamaño: {len(css)} bytes")

