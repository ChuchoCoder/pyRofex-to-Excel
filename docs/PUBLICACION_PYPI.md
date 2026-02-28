# Publicación en PyPI / TestPyPI

Sí, esta app se puede publicar como paquete pip.

## Estado actual del proyecto

El proyecto ya cuenta con lo esencial para empaquetado:
- `pyproject.toml` con metadata y dependencias
- build backend `setuptools`
- entrypoint CLI: `pyrofex-to-excel`
- layout `src/` compatible

## Recomendación de release

1. Probar build local

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

2. Publicar primero en TestPyPI (recomendado: workflow de GitHub)

- Ejecutar `Package Release` con `repository=testpypi`.
- El workflow usa Trusted Publishing (OIDC), sin tokens estáticos.

3. Probar instalación desde TestPyPI

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyrofex-to-excel
```

4. Publicar en PyPI

- Ejecutar `Package Release` con `repository=pypi`, o push de tag `v*`.

## Automatización con GitHub Actions

El repositorio ahora tiene dos workflows:

- CI (sin publicar): [.github/workflows/ci.yml](../.github/workflows/ci.yml)
	- Se ejecuta en `pull_request` y `push`.
	- Valida lint (si `ruff` está disponible), compilación (`compileall`) y build del paquete.
	- Ejecuta `twine check` para validar metadatos/render de distribución.

- Release de paquete: [.github/workflows/package-release.yml](../.github/workflows/package-release.yml)
	- Manual (`workflow_dispatch`) para elegir `testpypi` o `pypi`.
	- Automático a PyPI al pushear tags `v*`.
	- Publica con `pypa/gh-action-pypi-publish` + OIDC (Trusted Publishing).

## Credenciales y seguridad para publicación

- Método recomendado: Trusted Publishing (OIDC) desde GitHub Actions.
- No requiere `PYPI_API_TOKEN`/`TEST_PYPI_API_TOKEN` en GitHub Secrets.
- Configurar Trusted Publisher en PyPI/TestPyPI para este repo + workflow + environment.

Solo usar `twine upload` con token como fallback manual/local.

## Checklist previo recomendado

- [ ] Incrementar versión en `pyproject.toml`
- [ ] Verificar README renderiza bien en PyPI (`twine check`)
- [ ] Probar instalación limpia en venv nuevo
- [ ] Confirmar comandos `pyrofex-to-excel` y `python -m pyRofex_To_Excel` funcionan
- [ ] Confirmar dependencias nativas (Excel/xlwings) documentadas para usuarios Windows

## Limitación importante

Aunque el paquete pueda instalarse con pip, la operación real requiere:
- Windows
- Microsoft Excel instalado
- credenciales válidas de pyRofex

Eso debe estar muy claro en la descripción del paquete para reducir issues de instalación en entornos no compatibles.
