# Pruebas

## Ejecución de pruebas

Para ejecutar las pruebas, puedes usar pytest directamente o utilizar el script de conveniencia:

```bash
# Instalación de dependencias para desarrollo
pip install -e ".[dev]"

# directamente con pytest
pytest tests/
```

## Estructura de pruebas

Las pruebas están organizadas en el directorio `tests/` y utilizan pytest para una fácil automatización. Las pruebas se clasifican en:

- **Pruebas unitarias**: Prueban componentes individuales de la biblioteca
- **Pruebas de integración**: Prueban la interacción de múltiples componentes

## Cobertura de código

Para generar un informe de cobertura de código detallado:

```bash
pytest --cov=src --cov-report=html tests/
```

Esto generará un informe HTML en el directorio `htmlcov/`.
