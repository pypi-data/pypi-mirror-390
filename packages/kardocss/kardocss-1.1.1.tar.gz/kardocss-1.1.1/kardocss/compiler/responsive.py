"""
Generador de Variantes Responsive para KardoCSS

Este módulo maneja la generación de variantes responsive para todas las utilidades,
siguiendo el enfoque mobile-first con media queries min-width.
"""

import re
from typing import List, Dict, Tuple
from kardocss.core.config import KardoCSSConfig


class ResponsiveGenerator:
    """
    Generador de variantes responsive.
    
    Convierte utilidades base en variantes responsive con prefijos de breakpoint.
    Ejemplo: .k-flex -> .k-md\:flex
    """
    
    def __init__(self, config: KardoCSSConfig, prefix: str):
        """
        Inicializa el generador responsive.
        
        Args:
            config: Configuración de KardoCSS
            prefix: Prefijo de clases (ej: 'k-')
        """
        self.config = config
        self.prefix = prefix
        self.breakpoints = config.get("breakpoints", {})
        
        # Categorías que deben tener variantes responsive
        self.responsive_categories = {
            "layout", "spacing", "sizing", "typography", 
            "borders", "display", "effects"
        }
    
    def generate_responsive_variants(self, base_utilities: List[str]) -> List[str]:
        """
        Genera variantes responsive para las utilidades base.
        
        Args:
            base_utilities: Lista de strings CSS con utilidades base
            
        Returns:
            Lista de strings CSS con media queries y variantes responsive
        """
        variants = []
        
        # Parsear utilidades base
        parsed_utilities = self._parse_utilities(base_utilities)
        
        # Generar variantes para cada breakpoint
        for bp_name, bp_value in self.breakpoints.items():
            variants.append(f"@media (min-width: {bp_value}) {{")
            
            # Generar utilidades responsive para este breakpoint
            bp_utilities = self._create_breakpoint_utilities(
                parsed_utilities, bp_name
            )
            
            if bp_utilities:
                variants.extend(bp_utilities)
            else:
                # Placeholder si no hay utilidades (para mantener estructura)
                variants.append(f"  /* {bp_name} breakpoint utilities */")
            
            variants.append("}")
        
        return variants
    
    def _parse_utilities(self, utilities: List[str]) -> List[Dict]:
        """
        Parsea utilidades CSS en estructura de datos.
        
        Args:
            utilities: Lista de strings CSS
            
        Returns:
            Lista de diccionarios con selector y propiedades
        """
        parsed = []
        
        for line in utilities:
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith("/*") or line.startswith("*/"):
                continue
            
            # Parsear utilidad CSS
            utility = self._parse_css_line(line)
            if utility:
                parsed.append(utility)
        
        return parsed
    
    def _parse_css_line(self, line: str) -> Dict:
        """
        Parsea una línea CSS individual.
        
        Args:
            line: String con CSS (ej: ".k-flex { display: flex; }")
            
        Returns:
            Diccionario con selector y propiedades, o None si no se puede parsear
        """
        # Regex para capturar selector y propiedades
        # Captura: .selector { property: value; }
        pattern = r'\.([a-zA-Z0-9\-_:/\\]+)\s*\{\s*([^}]+)\s*\}'
        match = re.match(pattern, line)
        
        if match:
            selector = match.group(1)
            properties = match.group(2).strip()
            
            # Determinar si debe ser responsive
            should_be_responsive = self._should_be_responsive(selector)
            
            return {
                "selector": selector,
                "properties": properties,
                "responsive": should_be_responsive
            }
        
        return None
    
    def _should_be_responsive(self, selector: str) -> bool:
        """
        Determina si un selector debe tener variantes responsive.
        
        Args:
            selector: Selector CSS (sin el punto inicial)
            
        Returns:
            True si debe ser responsive, False en caso contrario
        """
        # Remover prefijo para análisis
        if selector.startswith(self.prefix):
            base_selector = selector[len(self.prefix):]
        else:
            base_selector = selector
        
        # Lista de patrones que deben ser responsive
        responsive_patterns = [
            # Layout
            r'^(flex|grid|block|inline|hidden)',
            r'^(flex-row|flex-col|flex-wrap)',
            r'^(justify-|items-|content-|self-)',
            r'^(grid-cols-|grid-rows-|col-span-|row-span-|gap-)',
            r'^(overflow-|visible|invisible)',
            
            # Spacing
            r'^(p-|px-|py-|pt-|pr-|pb-|pl-)',
            r'^(m-|mx-|my-|mt-|mr-|mb-|ml-)',
            
            # Sizing
            r'^(w-|h-|max-w-|max-h-|min-w-|min-h-)',
            
            # Typography
            r'^(text-xs|text-sm|text-base|text-lg|text-xl|text-2xl|text-3xl|text-4xl|text-5xl)',
            r'^(text-left|text-center|text-right|text-justify)',
            r'^(font-|leading-)',
            
            # Borders
            r'^(rounded-|border-\d)',
            
            # Display
            r'^(container)',
        ]
        
        # Verificar si coincide con algún patrón
        for pattern in responsive_patterns:
            if re.match(pattern, base_selector):
                return True
        
        return False
    
    def _create_breakpoint_utilities(
        self, 
        utilities: List[Dict], 
        breakpoint: str
    ) -> List[str]:
        """
        Crea utilidades responsive para un breakpoint específico.
        
        Args:
            utilities: Lista de utilidades parseadas
            breakpoint: Nombre del breakpoint (ej: 'md')
            
        Returns:
            Lista de strings CSS con utilidades responsive
        """
        responsive_utils = []
        
        for utility in utilities:
            if not utility.get("responsive", False):
                continue
            
            selector = utility["selector"]
            properties = utility["properties"]
            
            # Remover prefijo base si existe
            if selector.startswith(self.prefix):
                base_selector = selector[len(self.prefix):]
            else:
                base_selector = selector
            
            # Crear selector responsive con escape del ":"
            responsive_selector = f"{self.prefix}{breakpoint}\\:{base_selector}"
            
            # Generar CSS responsive
            responsive_css = f"  .{responsive_selector} {{ {properties} }}"
            responsive_utils.append(responsive_css)
        
        return responsive_utils
    
    def generate_container_responsive(self) -> List[str]:
        """
        Genera variantes responsive específicas para el container.
        
        Returns:
            Lista de strings CSS con media queries para container
        """
        variants = []
        
        container_config = config.get("container", {})
        max_widths = container_config.get("maxWidth", {})
        
        for bp_name, bp_value in self.breakpoints.items():
            if bp_name in max_widths:
                max_width = max_widths[bp_name]
                variants.append(f"@media (min-width: {bp_value}) {{")
                variants.append(f"  .{self.prefix}container {{ max-width: {max_width}; }}")
                variants.append("}")
        
        return variants


def generate_responsive_css(
    config: KardoCSSConfig, 
    prefix: str, 
    base_utilities: List[str]
) -> List[str]:
    """
    Función helper para generar CSS responsive.
    
    Args:
        config: Configuración de KardoCSS
        prefix: Prefijo de clases
        base_utilities: Utilidades base
        
    Returns:
        Lista de strings CSS con variantes responsive
    """
    generator = ResponsiveGenerator(config, prefix)
    return generator.generate_responsive_variants(base_utilities)

