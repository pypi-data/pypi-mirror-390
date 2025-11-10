"""Generador de Utilidades de Sizing (Width, Height, Max, Min)"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_sizing_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """Genera utilidades de tamaño."""
    utilities = []
    
    utilities.append("/* Sizing Utilities */")
    
    spacing = config.get("spacing", {})
    
    # Width
    for name, value in spacing.items():
        rem_value = value / 16 if value != 0 else 0
        utilities.append(f".{prefix}w-{name} {{ width: {rem_value}rem; }}")
    
    # Width especiales
    utilities.append(f".{prefix}w-auto {{ width: auto; }}")
    utilities.append(f".{prefix}w-full {{ width: 100%; }}")
    utilities.append(f".{prefix}w-screen {{ width: 100vw; }}")
    utilities.append(f".{prefix}w-min {{ width: min-content; }}")
    utilities.append(f".{prefix}w-max {{ width: max-content; }}")
    utilities.append(f".{prefix}w-fit {{ width: fit-content; }}")
    
    # Width fracciones
    fractions = [
        ("1/2", "50%"),
        ("1/3", "33.333333%"),
        ("2/3", "66.666667%"),
        ("1/4", "25%"),
        ("2/4", "50%"),
        ("3/4", "75%"),
        ("1/5", "20%"),
        ("2/5", "40%"),
        ("3/5", "60%"),
        ("4/5", "80%"),
        ("1/6", "16.666667%"),
        ("2/6", "33.333333%"),
        ("3/6", "50%"),
        ("4/6", "66.666667%"),
        ("5/6", "83.333333%"),
        ("1/12", "8.333333%"),
        ("2/12", "16.666667%"),
        ("3/12", "25%"),
        ("4/12", "33.333333%"),
        ("5/12", "41.666667%"),
        ("6/12", "50%"),
        ("7/12", "58.333333%"),
        ("8/12", "66.666667%"),
        ("9/12", "75%"),
        ("10/12", "83.333333%"),
        ("11/12", "91.666667%"),
    ]
    
    for name, value in fractions:
        utilities.append(f".{prefix}w-{name} {{ width: {value}; }}")
    
    # Height
    for name, value in spacing.items():
        rem_value = value / 16 if value != 0 else 0
        utilities.append(f".{prefix}h-{name} {{ height: {rem_value}rem; }}")
    
    # Height especiales
    utilities.append(f".{prefix}h-auto {{ height: auto; }}")
    utilities.append(f".{prefix}h-full {{ height: 100%; }}")
    utilities.append(f".{prefix}h-screen {{ height: 100vh; }}")
    utilities.append(f".{prefix}h-min {{ height: min-content; }}")
    utilities.append(f".{prefix}h-max {{ height: max-content; }}")
    utilities.append(f".{prefix}h-fit {{ height: fit-content; }}")
    
    # Height fracciones
    for name, value in fractions:
        utilities.append(f".{prefix}h-{name} {{ height: {value}; }}")
    
    # Max-Width
    max_widths = {
        "none": "none",
        "xs": "20rem",    # 320px
        "sm": "24rem",    # 384px
        "md": "28rem",    # 448px
        "lg": "32rem",    # 512px
        "xl": "36rem",    # 576px
        "2xl": "42rem",   # 672px
        "3xl": "48rem",   # 768px
        "4xl": "56rem",   # 896px
        "5xl": "64rem",   # 1024px
        "6xl": "72rem",   # 1152px
        "7xl": "80rem",   # 1280px
        "full": "100%",
    }
    
    for name, value in max_widths.items():
        utilities.append(f".{prefix}max-w-{name} {{ max-width: {value}; }}")
    
    # Max-Width basado en breakpoints
    breakpoints = config.get("breakpoints", {})
    for bp_name, bp_value in breakpoints.items():
        utilities.append(f".{prefix}max-w-screen-{bp_name} {{ max-width: {bp_value}; }}")
    
    # Max-Height
    max_heights = {
        "none": "none",
        "full": "100%",
        "screen": "100vh",
        "min": "min-content",
        "max": "max-content",
        "fit": "fit-content",
    }
    
    for name, value in max_heights.items():
        utilities.append(f".{prefix}max-h-{name} {{ max-height: {value}; }}")
    
    # Max-Height con spacing
    for name, value in spacing.items():
        rem_value = value / 16 if value != 0 else 0
        utilities.append(f".{prefix}max-h-{name} {{ max-height: {rem_value}rem; }}")
    
    # Min-Width
    min_widths = {
        "0": "0",
        "full": "100%",
        "min": "min-content",
        "max": "max-content",
        "fit": "fit-content",
    }
    
    for name, value in min_widths.items():
        utilities.append(f".{prefix}min-w-{name} {{ min-width: {value}; }}")
    
    # Min-Height
    min_heights = {
        "0": "0",
        "full": "100%",
        "screen": "100vh",
        "min": "min-content",
        "max": "max-content",
        "fit": "fit-content",
    }
    
    for name, value in min_heights.items():
        utilities.append(f".{prefix}min-h-{name} {{ min-height: {value}; }}")
    
    utilities.append("")
    return utilities

