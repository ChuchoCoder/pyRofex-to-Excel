# pyRofex-To-Excel

[![CI](https://github.com/ChuchoCoder/pyRofex_To_Excel/actions/workflows/ci.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex_To_Excel/actions/workflows/ci.yml)
[![Package Release](https://github.com/ChuchoCoder/pyRofex_To_Excel/actions/workflows/package-release.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex_To_Excel/actions/workflows/package-release.yml)

Aplicación Python para obtener datos de mercado en tiempo real desde pyRofex y volcarlos a Excel.

## 🚀 Correr desde cero (sin configuración previa)

Si acabás de clonar el repositorio y no tenés nada configurado, seguí exactamente estos pasos:

1. Requisitos mínimos
   - Windows + Microsoft Excel instalado
   - Python 3.9 o superior

2. Clonar e instalar

```bash
git clone https://github.com/ChuchoCoder/pyRofex_To_Excel.git
cd pyRofex_To_Excel
python -m venv .venv
.venv\Scripts\activate
pip install -e . --force-reinstall
```

3. Ejecutar por primera vez

```bash
python -m pyRofex_To_Excel
```

Qué pasa automáticamente en ese primer arranque:
- Si faltan credenciales, la app te las pide por consola y las guarda en `.env`.
- Si no existe workbook, crea uno nuevo (`.xlsx`) en la ruta configurada.
- Crea y prepara hojas base: `Tickers`, `MarketData`, `Trades`, `Formulas`.
- Intenta poblar `Tickers` con instrumentos desde caché local.

### 🗂️ Detalle exacto de preguntas en primer inicio

Si faltan credenciales obligatorias (`PYROFEX_USER`, `PYROFEX_PASSWORD`, `PYROFEX_ACCOUNT`), el bootstrap interactivo solicita en este orden:

1. `PYROFEX_USER`
2. `PYROFEX_PASSWORD` (input oculto)
3. `PYROFEX_ACCOUNT`
4. `PYROFEX_ENVIRONMENT` (default sugerido: `LIVE`)
5. `PYROFEX_API_URL` (default sugerido: `https://api.cocos.xoms.com.ar/`)
6. `PYROFEX_WS_URL` (default sugerido: `wss://api.cocos.xoms.com.ar/`)

Comportamiento importante:
- Si una variable ya tiene valor, aparece entre corchetes: `VARIABLE [valor_actual]:`
- Si presionás Enter y hay valor sugerido, se conserva.
- Si no hay valor sugerido en campos requeridos, vuelve a preguntar.
- Todo lo ingresado se persiste en `.env` automáticamente.

Ejemplo típico de consola:

```text
PYROFEX_USER: mi_usuario
PYROFEX_PASSWORD: ********
PYROFEX_ACCOUNT: mi_cuenta
PYROFEX_ENVIRONMENT [LIVE]:
PYROFEX_API_URL [https://api.cocos.xoms.com.ar/]:
PYROFEX_WS_URL [wss://api.cocos.xoms.com.ar/]:
```

Notas de operación:
- Si ejecutás en entorno no interactivo (ej. CI) y faltan credenciales, la app falla rápido y te pide setearlas en `.env`.
- Si el workbook configurado no existe y termina en `.xlsb`, el bootstrap lo normaliza a `.xlsx` para poder crearlo automáticamente.

4. Verificar que está funcionando
- Abrí el workbook generado.
- Confirmá que existen las hojas mencionadas.
- En `MarketData` deberían empezar a actualizarse precios.
- En `Formulas` tenés ejemplos listos para copy/paste con parámetros editables.

5. Si necesitás correr con script helper

```bash
.\setup.ps1 install
.\setup.ps1 run
```

También podés ejecutar por comando CLI del paquete:

```bash
pyrofex-to-excel
```

## 📌 Qué hace la app

- Suscribe instrumentos de `Tickers` contra pyRofex.
- Actualiza cotizaciones en `MarketData` (incluyendo cauciones).
- Sincroniza operaciones en `Trades` (modo periódico y opcional realtime).
- Evita escrituras innecesarias a Excel cuando no hay cambios (mejor performance).

## ⚙️ Configuración principal (`.env`)

Variables más usadas:

```env
EXCEL_FILE=pyRofex-Market-Data.xlsb
EXCEL_PATH=./
EXCEL_SHEET_PRICES=MarketData
EXCEL_SHEET_TICKERS=Tickers
EXCEL_SHEET_TRADES=Trades

EXCEL_UPDATE_INTERVAL=3.0

TRADES_SYNC_ENABLED=true
TRADES_REALTIME_ENABLED=false
TRADES_SYNC_INTERVAL_SECONDS=20
TRADES_BATCH_SIZE=500

PYROFEX_ENVIRONMENT=LIVE
PYROFEX_API_URL=https://api.cocos.xoms.com.ar/
PYROFEX_WS_URL=wss://api.cocos.xoms.com.ar/
PYROFEX_USER=REPLACE_WITH_YOUR_USERNAME
PYROFEX_PASSWORD=REPLACE_WITH_YOUR_PASSWORD
PYROFEX_ACCOUNT=REPLACE_WITH_YOUR_ACCOUNT
```

## 🧪 Validación rápida

```bash
python tools/validate_system.py
python tools/validate_quickstart.py
```

## 📚 Documentación nueva (español)

- Funcionalidades nuevas y cambios relevantes: [docs/FUNCIONALIDADES_NUEVAS.md](docs/FUNCIONALIDADES_NUEVAS.md)
- Publicación como paquete pip (PyPI/TestPyPI): [docs/PUBLICACION_PYPI.md](docs/PUBLICACION_PYPI.md)

## 📦 ¿Se puede publicar como paquete pip?

Sí. El proyecto ya está prácticamente listo para publicarse porque:
- tiene `pyproject.toml`
- define metadata de proyecto
- expone entrypoint CLI (`pyrofex-to-excel`)

Solo falta ejecutar el flujo de build + publicación (ver guía en [docs/PUBLICACION_PYPI.md](docs/PUBLICACION_PYPI.md)).

## 🔒 Seguridad

- Nunca subas `.env` con credenciales reales.
- Rotá credenciales periódicamente.
- Revisá permisos de archivos sensibles en tu entorno local.

