"""
Generador de utilidades de Gradientes para KardoCSS
"""

def generate_gradient_utilities(config):
    """Genera utilidades para gradientes de fondo"""
    css = []
    
    css.append("/* Gradientes */")
    
    # Gradientes de dirección
    directions = {
        'to-r': 'to right',
        'to-l': 'to left',
        'to-t': 'to top',
        'to-b': 'to bottom',
        'to-tr': 'to top right',
        'to-tl': 'to top left',
        'to-br': 'to bottom right',
        'to-bl': 'to bottom left',
    }
    
    # Colores para gradientes
    gradient_colors = {
        'blue': ('#dbeafe', '#3b82f6'),
        'purple': ('#f3e8ff', '#a855f7'),
        'pink': ('#fce7f3', '#ec4899'),
        'green': ('#d1fae5', '#10b981'),
        'yellow': ('#fef3c7', '#f59e0b'),
        'red': ('#fee2e2', '#ef4444'),
        'gray': ('#f3f4f6', '#6b7280'),
    }
    
    for dir_name, dir_value in directions.items():
        for color_name, (from_color, to_color) in gradient_colors.items():
            css.append(f"""
.k-bg-gradient-{dir_name}-{color_name} {{
    background-image: linear-gradient({dir_value}, {from_color}, {to_color});
}}
""")
    
    # Gradientes personalizados comunes
    css.append("""
/* Gradientes personalizados */
.k-bg-gradient-to-r {
    background-image: linear-gradient(to right, var(--gradient-from), var(--gradient-to, transparent));
}

.k-bg-gradient-to-l {
    background-image: linear-gradient(to left, var(--gradient-from), var(--gradient-to, transparent));
}

.k-bg-gradient-to-t {
    background-image: linear-gradient(to top, var(--gradient-from), var(--gradient-to, transparent));
}

.k-bg-gradient-to-b {
    background-image: linear-gradient(to bottom, var(--gradient-from), var(--gradient-to, transparent));
}

/* Colores de gradiente personalizables */
.k-from-blue-50 { --gradient-from: #eff6ff; }
.k-from-blue-100 { --gradient-from: #dbeafe; }
.k-to-blue-50 { --gradient-to: #eff6ff; }
.k-to-blue-100 { --gradient-to: #dbeafe; }

.k-from-purple-50 { --gradient-from: #faf5ff; }
.k-from-purple-100 { --gradient-from: #f3e8ff; }
.k-to-purple-50 { --gradient-to: #faf5ff; }
.k-to-purple-100 { --gradient-to: #f3e8ff; }

.k-from-pink-50 { --gradient-from: #fdf2f8; }
.k-from-pink-100 { --gradient-from: #fce7f3; }
.k-to-pink-50 { --gradient-to: #fdf2f8; }
.k-to-pink-100 { --gradient-to: #fce7f3; }

.k-from-green-50 { --gradient-from: #f0fdf4; }
.k-from-green-100 { --gradient-from: #dcfce7; }
.k-to-green-50 { --gradient-to: #f0fdf4; }
.k-to-green-100 { --gradient-to: #dcfce7; }
""")
    
    return '\n'.join(css)

