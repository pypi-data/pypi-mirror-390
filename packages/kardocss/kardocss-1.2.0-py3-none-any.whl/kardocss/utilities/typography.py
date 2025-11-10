"""
Generador de Utilidades de Tipografía
"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_typography_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """Genera utilidades de tipografía."""
    utilities = []
    
    utilities.append("/* Typography Utilities */")
    
    # Font sizes
    sizes = config.get("typography.sizes", {})
    for size_name, size_value in sizes.items():
        utilities.append(f".{prefix}text-{size_name} {{")
        utilities.append(f"  font-size: {size_value};")
        utilities.append("}")
    
    # Font weights
    weights = config.get("typography.weights", {})
    for weight_name, weight_value in weights.items():
        utilities.append(f".{prefix}font-{weight_name} {{")
        utilities.append(f"  font-weight: {weight_value};")
        utilities.append("}")
    
    # Text alignment
    for align in ["left", "center", "right", "justify"]:
        utilities.append(f".{prefix}text-{align} {{")
        utilities.append(f"  text-align: {align};")
        utilities.append("}")
    
    utilities.append("")
    return utilities

