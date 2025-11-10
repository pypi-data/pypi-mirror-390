"""
Container Queries Module for KardoCSS
Provides utilities for CSS Container Queries (@container)
Optimized for minimal size impact
"""

from kardocss.core.config import KardoCSSConfig

def generate():
    """Generate container query utilities (optimized)"""
    css = []
    config = KardoCSSConfig()
    prefix = config.get('prefix', 'k-')
    
    # Container type utilities
    css.append("""
/* Container Query Types */
.k-container-normal { container-type: normal; }
.k-container-size { container-type: size; }
.k-container-inline-size { container-type: inline-size; }
""")
    
    # Named containers (most common use cases)
    css.append("""
/* Named Containers */
.k-container-card { container-name: card; container-type: inline-size; }
.k-container-sidebar { container-name: sidebar; container-type: inline-size; }
.k-container-main { container-name: main; container-type: inline-size; }
""")
    
    # Container query breakpoints (only essential ones)
    # Reduced from 10 to 4 breakpoints to minimize CSS size
    breakpoints = {
        'sm': '24rem',   # 384px - Mobile landscape / Small tablets
        'md': '32rem',   # 512px - Tablets
        'lg': '48rem',   # 768px - Desktop
        'xl': '64rem',   # 1024px - Large desktop
    }
    
    # Generate only ESSENTIAL container query utilities
    for bp_name, bp_value in breakpoints.items():
        css.append(f"\n/* Container Query: {bp_name} (min-width: {bp_value}) */")
        css.append(f"@container (min-width: {bp_value}) {{")
        
        # Display utilities (most used)
        css.append(f"  .k-cq-{bp_name}\\:block {{ display: block; }}")
        css.append(f"  .k-cq-{bp_name}\\:flex {{ display: flex; }}")
        css.append(f"  .k-cq-{bp_name}\\:grid {{ display: grid; }}")
        css.append(f"  .k-cq-{bp_name}\\:hidden {{ display: none; }}")
        
        # Flex direction
        css.append(f"  .k-cq-{bp_name}\\:flex-row {{ flex-direction: row; }}")
        css.append(f"  .k-cq-{bp_name}\\:flex-col {{ flex-direction: column; }}")
        
        # Grid columns (only most common)
        for cols in [1, 2, 3, 4]:
            css.append(f"  .k-cq-{bp_name}\\:grid-cols-{cols} {{ grid-template-columns: repeat({cols}, minmax(0, 1fr)); }}")
        
        # Gap utilities (only essential sizes)
        essential_gaps = {'2': 8, '4': 16, '6': 24, '8': 32}
        for size, px_value in essential_gaps.items():
            rem_value = f"{px_value / 16}rem"
            css.append(f"  .k-cq-{bp_name}\\:gap-{size} {{ gap: {rem_value}; }}")
        
        # Padding utilities (only essential sizes)
        for size, px_value in essential_gaps.items():
            rem_value = f"{px_value / 16}rem"
            css.append(f"  .k-cq-{bp_name}\\:p-{size} {{ padding: {rem_value}; }}")
        
        # Text alignment
        css.append(f"  .k-cq-{bp_name}\\:text-left {{ text-align: left; }}")
        css.append(f"  .k-cq-{bp_name}\\:text-center {{ text-align: center; }}")
        css.append(f"  .k-cq-{bp_name}\\:text-right {{ text-align: right; }}")
        
        # Text sizes (only essential)
        essential_text = {
            'sm': '0.875rem',
            'base': '1rem',
            'lg': '1.125rem',
            'xl': '1.25rem',
        }
        for size, value in essential_text.items():
            css.append(f"  .k-cq-{bp_name}\\:text-{size} {{ font-size: {value}; }}")
        
        css.append("}")
    
    return '\n'.join(css)

