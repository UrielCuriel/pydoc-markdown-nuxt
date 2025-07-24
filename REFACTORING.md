# Refactorización de pruebas a pytest

Este documento resume los cambios realizados para refactorizar las pruebas a pytest.

## Cambios principales

1. **Estructura de directorios**:
   - Creación del directorio `tests/` para organizar todas las pruebas
   - Traslado y refactorización de los archivos de prueba existentes

2. **Configuración de pytest**:
   - Creación de `conftest.py` con fixtures compartidos
   - Creación de `pytest.ini` para configuración global
   - Actualización de `pyproject.toml` para incluir pytest como dependencia

3. **Mejoras en las pruebas**:
   - Uso de fixtures de pytest para compartir recursos entre pruebas
   - Reemplazo de funciones `print` por aserciones pytest
   - Organización de pruebas en categorías con marcas (unit/integration)
   - Inclusión de comentarios explicativos

4. **Automatización**:
   - Script `run_tests.py` para facilitar la ejecución de todas las pruebas
   - Configuración para generación de informes de cobertura
   - Documentación en `TESTING.md`

## Archivos refactorizados

- test_mdc_simple.py
- test_comprehensive_mdc.py
- test_mdc_args.py
- test_configuration.py
- test_integration.py
- test_renderer.py
- test_resolver.py
- test_utils.py

## Nuevos archivos

- conftest.py
- pytest.ini
- run_tests.py
- TESTING.md
- tests/ (directorio)
  - [todos los archivos refactorizados]

## Notas adicionales

- Se ha mantenido la funcionalidad original de todas las pruebas
- Los test ahora son más fáciles de ejecutar y mantener
- La refactorización facilita añadir nuevas pruebas en el futuro
