"""
Generador de utilidades de Badges para KardoCSS
"""

def generate_badge_utilities(config):
    """Genera utilidades para badges y etiquetas"""
    css = []
    
    css.append("/* Badges y Etiquetas */")
    
    # Badge base
    css.append("""
.k-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
}
""")
    
    # Badge con colores
    colors = config.get('colors', {})
    for color_name, color_value in colors.items():
        if color_name in ['primary', 'secondary', 'success', 'warning', 'danger']:
            css.append(f"""
.k-badge-{color_name} {{
    background-color: {color_value};
    color: white;
}}
""")
    
    # Badge con colores de fondo claros
    css.append("""
.k-badge-light {
    background-color: #f3f4f6;
    color: #374151;
}

.k-badge-dark {
    background-color: #1f2937;
    color: white;
}
""")
    
    return '\n'.join(css)

