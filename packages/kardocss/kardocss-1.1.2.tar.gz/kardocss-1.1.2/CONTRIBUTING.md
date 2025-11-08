# Contribuir a KardoCSS

¡Gracias por tu interés en contribuir a KardoCSS! Este documento proporciona pautas para contribuir al proyecto.

## Código de Conducta

Al participar en este proyecto, te comprometes a mantener un ambiente respetuoso y colaborativo.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue con:

- Descripción clara del problema
- Código CSS/HTML que reproduce el issue
- Comportamiento esperado vs actual
- Navegador y versión (si es relevante)

### Sugerir Nuevas Utilidades

Las sugerencias de nuevas utilidades CSS son bienvenidas. Por favor:

- Verifica que no exista una utilidad similar
- Describe claramente la utilidad propuesta
- Proporciona casos de uso
- Incluye ejemplo de código

### Pull Requests

1. **Fork el repositorio**
2. **Crea una rama** para tu feature (`git checkout -b feature/NewUtility`)
3. **Commits con mensajes claros**
4. **Agrega tests** si es aplicable
5. **Actualiza la documentación**
6. **Compila el CSS** para verificar que funciona
7. **Push a tu fork**
8. **Abre un Pull Request**

### Estándares de Código

#### Python (Compilador)
- **Python 3.14+**
- **PEP 8** para estilo
- **Type hints** en funciones
- **Docstrings** claros

#### CSS Generado
- **Mobile-first** siempre
- **Prefijo k-** en todas las clases
- **Nombres descriptivos** y consistentes
- **Comentarios** para secciones complejas

### Agregar Nueva Utilidad

1. Crea o modifica el archivo en `kardocss/utilities/`
2. Agrega la función generadora
3. Registra en el compilador
4. Agrega tests
5. Actualiza documentación
6. Compila y verifica

Ejemplo:

```python
# kardocss/utilities/mi_utilidad.py
def generate_mi_utilidad(config, prefix):
    utilities = []
    utilities.append(f".{prefix}mi-clase {{ propiedad: valor; }}")
    return utilities
```

### Tests

```bash
# Ejecutar tests
pytest

# Compilar CSS de prueba
python -m kardocss.cli.build --output test.css
```

### Documentación

- Actualiza README.md con nuevas utilidades
- Agrega ejemplos de uso
- Documenta opciones de configuración

## Proceso de Revisión

1. Un mantenedor revisará tu PR
2. Se pueden solicitar cambios
3. Una vez aprobado, se hará merge

## Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la licencia MIT del proyecto.

