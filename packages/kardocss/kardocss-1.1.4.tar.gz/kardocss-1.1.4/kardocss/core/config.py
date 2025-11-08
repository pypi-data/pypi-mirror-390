"""
Sistema de Configuración de KardoCSS

Define los colores, espaciados, breakpoints y otras configuraciones
del framework CSS.
"""

from typing import Dict, List, Any


class KardoCSSConfig:
    """
    Configuración principal de KardoCSS.
    
    Define todos los tokens de diseño: colores, espaciados, tipografía,
    breakpoints, etc.
    """
    
    def __init__(self, custom_config: Dict[str, Any] = None):
        """
        Inicializa la configuración con valores por defecto.
        
        Args:
            custom_config: Configuración personalizada para sobrescribir defaults
        """
        self.config = self._get_default_config()
        
        if custom_config:
            self._merge_config(custom_config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna la configuración por defecto de KardoCSS."""
        return {
            # Prefijo para todas las clases
            "prefix": "k-",
            
            # Colores del sistema
            "colors": {
                # Colores principales
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "success": "#27ae60",
                "warning": "#f39c12",
                "danger": "#c0392b",
                "info": "#3498db",
                
                # Colores neutros
                "white": "#ffffff",
                "black": "#000000",
                
                # Escala de grises
                "gray": {
                    "100": "#f8f9fa",
                    "200": "#e9ecef",
                    "300": "#dee2e6",
                    "400": "#ced4da",
                    "500": "#adb5bd",
                    "600": "#6c757d",
                    "700": "#495057",
                    "800": "#343a40",
                    "900": "#212529",
                },
            },
            
            # Escala de espaciado (en px, se convertirá a rem)
            "spacing": {
                "0": 0,
                "1": 4,
                "2": 8,
                "3": 12,
                "4": 16,
                "5": 20,
                "6": 24,
                "8": 32,
                "10": 40,
                "12": 48,
                "16": 64,
                "20": 80,
                "24": 96,
                "32": 128,
            },
            
            # Tipografía
            "typography": {
                # Tamaños de fuente
                "sizes": {
                    "xs": "0.75rem",    # 12px
                    "sm": "0.875rem",   # 14px
                    "base": "1rem",     # 16px
                    "lg": "1.125rem",   # 18px
                    "xl": "1.25rem",    # 20px
                    "2xl": "1.5rem",    # 24px
                    "3xl": "1.875rem",  # 30px
                    "4xl": "2.25rem",   # 36px
                    "5xl": "3rem",      # 48px
                },
                
                # Pesos de fuente
                "weights": {
                    "thin": 100,
                    "light": 300,
                    "normal": 400,
                    "medium": 500,
                    "semibold": 600,
                    "bold": 700,
                    "black": 900,
                },
                
                # Familias de fuente
                "families": {
                    "sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                    "serif": "Georgia, Cambria, 'Times New Roman', Times, serif",
                    "mono": "Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
                },
                
                # Line heights
                "lineHeights": {
                    "none": 1,
                    "tight": 1.25,
                    "snug": 1.375,
                    "normal": 1.5,
                    "relaxed": 1.625,
                    "loose": 2,
                },
            },
            
            # Breakpoints (mobile-first)
            "breakpoints": {
                "sm": "640px",   # Teléfonos grandes
                "md": "768px",   # Tablets
                "lg": "1024px",  # Laptops
                "xl": "1280px",  # Desktops
                "2xl": "1536px", # Desktops grandes
            },
            
            # Border radius
            "borderRadius": {
                "none": "0",
                "sm": "0.125rem",   # 2px
                "DEFAULT": "0.25rem",  # 4px
                "md": "0.375rem",   # 6px
                "lg": "0.5rem",     # 8px
                "xl": "0.75rem",    # 12px
                "2xl": "1rem",      # 16px
                "full": "9999px",
            },
            
            # Sombras
            "shadows": {
                "none": "none",
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "DEFAULT": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            },
            
            # Z-index
            "zIndex": {
                "0": 0,
                "10": 10,
                "20": 20,
                "30": 30,
                "40": 40,
                "50": 50,
                "auto": "auto",
            },
            
            # Opacidad
            "opacity": {
                "0": "0",
                "25": "0.25",
                "50": "0.5",
                "75": "0.75",
                "100": "1",
            },
            
            # Container
            "container": {
                "center": True,
                "padding": "1rem",
                "maxWidth": {
                    "sm": "640px",
                    "md": "768px",
                    "lg": "1024px",
                    "xl": "1280px",
                    "2xl": "1536px",
                },
            },
        }
    
    def _merge_config(self, custom_config: Dict[str, Any]) -> None:
        """
        Combina la configuración personalizada con la por defecto.
        
        Args:
            custom_config: Configuración personalizada
        """
        def deep_merge(base: dict, custom: dict) -> dict:
            """Merge recursivo de diccionarios."""
            result = base.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config = deep_merge(self.config, custom_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            key: Clave de configuración (soporta notación de punto)
            default: Valor por defecto si la clave no existe
        
        Returns:
            Valor de configuración
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave de configuración (soporta notación de punto)
            value: Valor a establecer
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna la configuración completa como diccionario."""
        return self.config.copy()
    
    @classmethod
    def from_file(cls, filepath: str) -> 'KardoCSSConfig':
        """
        Carga configuración desde un archivo Python.
        
        Args:
            filepath: Path al archivo de configuración
        
        Returns:
            Instancia de KardoCSSConfig
        """
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("config", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        custom_config = getattr(module, "config", {})
        return cls(custom_config)


# Configuración por defecto
default_config = KardoCSSConfig()

