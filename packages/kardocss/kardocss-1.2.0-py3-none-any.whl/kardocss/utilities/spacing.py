"""
Generador de Utilidades de Espaciado

Genera clases para margin y padding en todas las direcciones.
"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_spacing_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """
    Genera utilidades de espaciado (margin y padding).
    
    Args:
        config: Configuración de KardoCSS
        prefix: Prefijo para las clases (ej: 'k-')
    
    Returns:
        Lista de reglas CSS
    """
    utilities = []
    spacing_scale = config.get("spacing", {})
    
    # Tipos de espaciado
    spacing_types = {
        "p": "padding",
        "m": "margin",
    }
    
    # Direcciones
    directions = {
        "": ["top", "right", "bottom", "left"],  # Todos los lados
        "x": ["left", "right"],                   # Horizontal
        "y": ["top", "bottom"],                   # Vertical
        "t": ["top"],                             # Top
        "r": ["right"],                           # Right
        "b": ["bottom"],                          # Bottom
        "l": ["left"],                            # Left
    }
    
    utilities.append("/* Spacing Utilities */")
    
    for type_key, type_name in spacing_types.items():
        for dir_key, dir_values in directions.items():
            for size_key, size_value in spacing_scale.items():
                # Convertir px a rem (16px = 1rem)
                size_rem = f"{size_value / 16}rem" if size_value > 0 else "0"
                
                # Nombre de la clase
                class_name = f"{prefix}{type_key}{dir_key}-{size_key}"
                
                # Generar regla CSS
                utilities.append(f".{class_name} {{")
                
                for direction in dir_values:
                    utilities.append(f"  {type_name}-{direction}: {size_rem};")
                
                utilities.append("}")
    
    # Margin auto
    utilities.append(f".{prefix}mx-auto {{")
    utilities.append("  margin-left: auto;")
    utilities.append("  margin-right: auto;")
    utilities.append("}")
    
    utilities.append(f".{prefix}my-auto {{")
    utilities.append("  margin-top: auto;")
    utilities.append("  margin-bottom: auto;")
    utilities.append("}")
    
    utilities.append("")
    return utilities

