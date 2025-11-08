"""
Generador de Utilidades de Colores

Genera clases para background, text y border colors.
"""

from typing import List, Dict, Any
from kardocss.core.config import KardoCSSConfig


def generate_color_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """
    Genera utilidades de colores.
    
    Args:
        config: Configuración de KardoCSS
        prefix: Prefijo para las clases
    
    Returns:
        Lista de reglas CSS
    """
    utilities = []
    colors = config.get("colors", {})
    
    utilities.append("/* Color Utilities */")
    
    # Función helper para procesar colores
    def process_colors(color_dict: Dict[str, Any], parent_key: str = ""):
        """Procesa colores recursivamente para manejar escalas."""
        result = {}
        
        for key, value in color_dict.items():
            if isinstance(value, dict):
                # Es una escala de colores (ej: gray.100, gray.200)
                nested = process_colors(value, key)
                for nested_key, nested_value in nested.items():
                    result[f"{key}-{nested_key}"] = nested_value
            else:
                # Es un color simple
                result[key] = value
        
        return result
    
    # Procesar colores
    flat_colors = process_colors(colors)
    
    # Background colors
    utilities.append("/* Background Colors */")
    for color_name, color_value in flat_colors.items():
        utilities.append(f".{prefix}bg-{color_name} {{")
        utilities.append(f"  background-color: {color_value};")
        utilities.append("}")
    
    # Text colors
    utilities.append("")
    utilities.append("/* Text Colors */")
    for color_name, color_value in flat_colors.items():
        utilities.append(f".{prefix}text-{color_name} {{")
        utilities.append(f"  color: {color_value};")
        utilities.append("}")
    
    # Border colors
    utilities.append("")
    utilities.append("/* Border Colors */")
    for color_name, color_value in flat_colors.items():
        utilities.append(f".{prefix}border-{color_name} {{")
        utilities.append(f"  border-color: {color_value};")
        utilities.append("}")
    
    utilities.append("")
    return utilities

