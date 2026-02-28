# Instalación y uso sin clonar el repositorio

Esta guía es para usar `pyrofex-to-excel` como usuario final, instalando desde PyPI.

## Requisitos

- Windows
- Microsoft Excel instalado
- Python 3.9 o superior

## Instalación limpia (recomendada)

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pyrofex-to-excel
```

## Primer arranque

Ejecutá:

```bash
pyrofex-to-excel
```

Alternativa equivalente:

```bash
python -m pyRofex_To_Excel
```

En el primer arranque:
- Si faltan credenciales, la app las solicita por consola y persiste en `.env`.
- Si no existe workbook, crea uno nuevo (`.xlsx`) en la ruta configurada.
- Crea hojas base: `Tickers`, `MarketData`, `Trades`, `Formulas`.

## Variables más usadas en `.env`

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

## Actualizar a una versión más nueva

```bash
python -m pip install --upgrade pyrofex-to-excel
```

## Desinstalar

```bash
python -m pip uninstall pyrofex-to-excel
```

## Problemas comunes

- El comando `pyrofex-to-excel` no se reconoce:
  - Verificá que el entorno virtual esté activado (`.venv\Scripts\activate`).
- No se crea el `.xlsb` en primer arranque:
  - Es esperado; si no existe workbook, se crea `.xlsx` para bootstrap automático.

## Nota para desarrolladores (TestPyPI)

TestPyPI se usa solo para testing (por ejemplo, builds de PR), no para usuarios finales.

Si necesitás instalar un build de prueba:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyrofex-to-excel
```

## Seguridad

- No compartas ni publiques `.env` con credenciales reales.
- Rotá credenciales periódicamente.
