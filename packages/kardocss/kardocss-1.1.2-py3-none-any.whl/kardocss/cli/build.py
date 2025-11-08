#!/usr/bin/env python3
"""
KardoCSS Build CLI

Herramienta de línea de comandos para compilar KardoCSS.
"""

import argparse
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kardocss import KardoCSSConfig, KardoCSSCompiler


def main():
    """Punto de entrada principal del CLI."""
    parser = argparse.ArgumentParser(
        description="KardoCSS - Compilador de Framework CSS Mobile-First",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Compilar con configuración por defecto
  python -m kardocss.cli.build -o dist/kardocss.css
  
  # Compilar y minificar
  python -m kardocss.cli.build -o dist/kardocss.min.css --minify
  
  # Usar configuración personalizada
  python -m kardocss.cli.build -c kardocss.config.py -o dist/kardocss.css
        """
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Archivo de salida para el CSS compilado"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Archivo de configuración personalizada (Python)"
    )
    
    parser.add_argument(
        "-m", "--minify",
        action="store_true",
        help="Minificar el CSS de salida"
    )
    
    parser.add_argument(
        "--purge",
        nargs="+",
        help="Archivos HTML/templates para purging de CSS no utilizado"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mostrar información detallada"
    )
    
    args = parser.parse_args()
    
    try:
        # Cargar configuración
        if args.config:
            if args.verbose:
                print(f"📝 Cargando configuración desde: {args.config}")
            config = KardoCSSConfig.from_file(args.config)
        else:
            if args.verbose:
                print("📝 Usando configuración por defecto")
            config = KardoCSSConfig()
        
        # Crear compilador
        compiler = KardoCSSCompiler(config)
        
        # Compilar
        if args.verbose:
            print("🔨 Compilando KardoCSS...")
        
        compiler.compile_to_file(
            output_path=args.output,
            minify=args.minify
        )
        
        # Mensaje de éxito
        output_path = Path(args.output)
        size_kb = output_path.stat().st_size / 1024
        
        print(f"\n✅ Compilación exitosa!")
        print(f"📦 Archivo: {args.output}")
        print(f"📏 Tamaño: {size_kb:.2f} KB")
        
        if args.minify:
            print("🗜️  Minificado: Sí")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error durante la compilación: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

