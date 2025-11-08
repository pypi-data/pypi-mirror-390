"""Generador de Utilidades de Bordes"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_border_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """Genera utilidades de bordes."""
    utilities = []
    
    utilities.append("/* Border Utilities */")
    
    # Border radius
    radius = config.get("borderRadius", {})
    for radius_name, radius_value in radius.items():
        class_name = f"{prefix}rounded" if radius_name == "DEFAULT" else f"{prefix}rounded-{radius_name}"
        utilities.append(f".{class_name} {{ border-radius: {radius_value}; }}")
    
    # Shadows
    shadows = config.get("shadows", {})
    for shadow_name, shadow_value in shadows.items():
        class_name = f"{prefix}shadow" if shadow_name == "DEFAULT" else f"{prefix}shadow-{shadow_name}"
        utilities.append(f".{class_name} {{ box-shadow: {shadow_value}; }}")
    
    utilities.append("")
    return utilities

