"""
Generador de Utilidades de Efectos (Shadows, Opacity, Transitions, Animations)
Refactorizado para integrarse con el compilador de KardoCSS
"""

from typing import List
from kardocss.core.config import KardoCSSConfig


def generate_effect_utilities(config: KardoCSSConfig, prefix: str) -> List[str]:
    """Genera utilidades de efectos visuales."""
    utilities = []
    
    utilities.append("/* Effect Utilities */")
    
    # Shadows
    shadows = config.get("shadows", {})
    for name, value in shadows.items():
        if name == "DEFAULT":
            utilities.append(f".{prefix}shadow {{ box-shadow: {value}; }}")
        else:
            utilities.append(f".{prefix}shadow-{name} {{ box-shadow: {value}; }}")
    
    # Shadow inner
    utilities.append(f".{prefix}shadow-inner {{ box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06); }}")
    
    # Opacity
    opacities = config.get("opacity", {})
    for name, value in opacities.items():
        utilities.append(f".{prefix}opacity-{name} {{ opacity: {value}; }}")
    
    # Opacidades adicionales
    utilities.append(f".{prefix}opacity-80 {{ opacity: 0.8; }}")
    utilities.append(f".{prefix}opacity-90 {{ opacity: 0.9; }}")
    utilities.append(f".{prefix}opacity-95 {{ opacity: 0.95; }}")
    
    # Z-index
    z_indexes = config.get("zIndex", {})
    for name, value in z_indexes.items():
        utilities.append(f".{prefix}z-{name} {{ z-index: {value}; }}")
    
    # Transitions
    utilities.append(f".{prefix}transition-none {{ transition-property: none; }}")
    utilities.append(f".{prefix}transition {{ transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow, transform; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    utilities.append(f".{prefix}transition-all {{ transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    utilities.append(f".{prefix}transition-colors {{ transition-property: background-color, border-color, color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    utilities.append(f".{prefix}transition-opacity {{ transition-property: opacity; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    utilities.append(f".{prefix}transition-shadow {{ transition-property: box-shadow; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    utilities.append(f".{prefix}transition-transform {{ transition-property: transform; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }}")
    
    # Duration
    durations = [75, 100, 150, 200, 300, 500, 700, 1000]
    for duration in durations:
        utilities.append(f".{prefix}duration-{duration} {{ transition-duration: {duration}ms; }}")
    
    # Delay (v1.1.1 - Issue #1)
    delays = [75, 100, 150, 200, 300, 500, 700, 1000]
    for delay in delays:
        utilities.append(f".{prefix}delay-{delay} {{ transition-delay: {delay}ms; }}")
    
    # Timing functions
    utilities.append(f".{prefix}ease-linear {{ transition-timing-function: linear; }}")
    utilities.append(f".{prefix}ease-in {{ transition-timing-function: cubic-bezier(0.4, 0, 1, 1); }}")
    utilities.append(f".{prefix}ease-out {{ transition-timing-function: cubic-bezier(0, 0, 0.2, 1); }}")
    utilities.append(f".{prefix}ease-in-out {{ transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }}")
    
    # Additional easing functions (v1.1.1 - Issue #1)
    utilities.append(f".{prefix}ease-bounce {{ transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55); }}")
    utilities.append(f".{prefix}ease-back-in {{ transition-timing-function: cubic-bezier(0.6, -0.28, 0.735, 0.045); }}")
    utilities.append(f".{prefix}ease-back-out {{ transition-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1.275); }}")
    utilities.append(f".{prefix}ease-back-in-out {{ transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55); }}")
    
    # Transform utilities (fixed to apply transform directly)
    # Scale
    scales = [0, 50, 75, 90, 95, 100, 105, 110, 125, 150]
    for scale in scales:
        scale_value = scale / 100
        utilities.append(f".{prefix}scale-{scale} {{ transform: scale({scale_value}); }}")
    
    # Rotate
    rotations = [0, 45, 90, 180]
    for rotation in rotations:
        utilities.append(f".{prefix}rotate-{rotation} {{ transform: rotate({rotation}deg); }}")
        if rotation > 0:
            utilities.append(f".{prefix}-rotate-{rotation} {{ transform: rotate(-{rotation}deg); }}")
    
    # Translate
    translates = [0, 1, 2, 3, 4, 6, 8, 12, 16]
    for translate in translates:
        translate_value = translate * 0.25  # 0.25rem per unit
        utilities.append(f".{prefix}translate-x-{translate} {{ transform: translateX({translate_value}rem); }}")
        utilities.append(f".{prefix}translate-y-{translate} {{ transform: translateY({translate_value}rem); }}")
        if translate > 0:
            utilities.append(f".{prefix}-translate-x-{translate} {{ transform: translateX(-{translate_value}rem); }}")
            utilities.append(f".{prefix}-translate-y-{translate} {{ transform: translateY(-{translate_value}rem); }}")
    
    # Cursor
    cursors = ["auto", "default", "pointer", "wait", "text", "move", "not-allowed"]
    for cursor in cursors:
        utilities.append(f".{prefix}cursor-{cursor} {{ cursor: {cursor}; }}")
    
    # User Select
    utilities.append(f".{prefix}select-none {{ user-select: none; }}")
    utilities.append(f".{prefix}select-text {{ user-select: text; }}")
    utilities.append(f".{prefix}select-all {{ user-select: all; }}")
    utilities.append(f".{prefix}select-auto {{ user-select: auto; }}")
    
    # Pointer Events
    utilities.append(f".{prefix}pointer-events-none {{ pointer-events: none; }}")
    utilities.append(f".{prefix}pointer-events-auto {{ pointer-events: auto; }}")
    
    # Blur
    utilities.append(f".{prefix}blur-none {{ filter: blur(0); }}")
    utilities.append(f".{prefix}blur-sm {{ filter: blur(4px); }}")
    utilities.append(f".{prefix}blur {{ filter: blur(8px); }}")
    utilities.append(f".{prefix}blur-md {{ filter: blur(12px); }}")
    utilities.append(f".{prefix}blur-lg {{ filter: blur(16px); }}")
    utilities.append(f".{prefix}blur-xl {{ filter: blur(24px); }}")
    
    # Backdrop Blur
    utilities.append(f".{prefix}backdrop-blur-none {{ backdrop-filter: blur(0); }}")
    utilities.append(f".{prefix}backdrop-blur-sm {{ backdrop-filter: blur(4px); }}")
    utilities.append(f".{prefix}backdrop-blur {{ backdrop-filter: blur(8px); }}")
    utilities.append(f".{prefix}backdrop-blur-md {{ backdrop-filter: blur(12px); }}")
    utilities.append(f".{prefix}backdrop-blur-lg {{ backdrop-filter: blur(16px); }}")
    utilities.append(f".{prefix}backdrop-blur-xl {{ backdrop-filter: blur(24px); }}")
    
    # Animations (keyframes)
    utilities.append("")
    utilities.append("/* Keyframe Animations */")
    utilities.append("@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }")
    utilities.append("@keyframes ping { 75%, 100% { transform: scale(2); opacity: 0; } }")
    utilities.append("@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }")
    utilities.append("@keyframes bounce { 0%, 100% { transform: translateY(-25%); animation-timing-function: cubic-bezier(0.8, 0, 1, 1); } 50% { transform: translateY(0); animation-timing-function: cubic-bezier(0, 0, 0.2, 1); } }")
    utilities.append("@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }")
    utilities.append("@keyframes slide-in-up { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }")
    utilities.append("@keyframes slide-in-down { from { transform: translateY(-100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }")
    
    # Animation classes
    utilities.append(f".{prefix}animate-spin {{ animation: spin 1s linear infinite; }}")
    utilities.append(f".{prefix}animate-ping {{ animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite; }}")
    utilities.append(f".{prefix}animate-pulse {{ animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}")
    utilities.append(f".{prefix}animate-bounce {{ animation: bounce 1s infinite; }}")
    utilities.append(f".{prefix}animate-fade-in {{ animation: fade-in 0.5s ease-out; }}")
    utilities.append(f".{prefix}animate-slide-in-up {{ animation: slide-in-up 0.5s ease-out; }}")
    utilities.append(f".{prefix}animate-slide-in-down {{ animation: slide-in-down 0.5s ease-out; }}")
    
    utilities.append("")
    return utilities


# Mantener compatibilidad con versión anterior
def generate_effects():
    """Función legacy para compatibilidad"""
    from kardocss.core.config import KardoCSSConfig
    config = KardoCSSConfig()
    utilities = generate_effect_utilities(config, "k-")
    return "\n".join(utilities)

