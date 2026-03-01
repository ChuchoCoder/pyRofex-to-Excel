# pyRofex-to-Excel

[![CI](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml)
[![Package Release](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml)

Aplicación Python para obtener datos de mercado en tiempo real desde pyRofex y volcarlos a Excel.

## 🚀 Correr desde cero (paquete publicado en PyPI)

Si solo querés usar la app (sin clonar el repo), este es el camino más simple.

1. Requisitos mínimos
   - Windows + Microsoft Excel instalado
   - Python 3.9 o superior

2. Instalar el paquete (rápido, sin `.venv`)

```bash
python -m pip install --user pyrofex-to-excel
```

3. Ejecutar la app

```bash
pyrofex-to-excel
```

Ver versión instalada:

```bash
pyrofex-to-excel --version
```

Alternativa equivalente:

```bash
python -m pyRofex_To_Excel
```

Opcional (recomendado si querés aislamiento de dependencias): usar `.venv`

```bash
mkdir pyrofex-app
cd pyrofex-app
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pyrofex-to-excel
```

Qué pasa automáticamente en ese primer arranque:
- Si faltan credenciales, la app te las pide por consola y las guarda en `.env`.
- Si no existe workbook, crea uno nuevo (`.xlsx`) en la ruta configurada.
- Crea y prepara hojas base: `Tickers`, `MarketData`, `Trades`, `Formulas`.
- Intenta poblar `Tickers` con instrumentos desde caché local.

Si necesitás volver a ejecutar ese asistente (por ejemplo, usuario/clave incorrectos):

```bash
pyrofex-to-excel --reconfigure
```

4. Verificar que está funcionando
- Abrí el workbook generado.
- Confirmá que existen las hojas `Tickers`, `MarketData`, `Trades` y `Formulas`.
- En `MarketData` deberían empezar a actualizarse precios.

Para guía completa sin clonar (actualización/desinstalación), ver [docs/INSTALACION_SIN_CLONAR.md](docs/INSTALACION_SIN_CLONAR.md).

## 🛠️ Correr con repositorio clonado (modo desarrollo)

Si vas a desarrollar en este proyecto:

```bash
git clone https://github.com/ChuchoCoder/pyRofex-to-Excel.git
cd pyRofex-to-Excel
python -m venv .venv
.venv\Scripts\activate
pip install -e . --force-reinstall
python -m pyRofex_To_Excel
```

### 📦 Nota para desarrolladores: TestPyPI

TestPyPI se usa solo para pruebas de CI/CD (por ejemplo, builds de PR) y no para usuarios finales.

Si necesitás instalar un build de testing:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyrofex-to-excel
```

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

Nota sobre contraseña:
- En Windows, al escribir `PYROFEX_PASSWORD` se muestra `*` por cada carácter.
- En otros sistemas, puede mostrarse como input oculto según el terminal.

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

### ⚡ Atajos opcionales (desarrollo)

Si preferís usar script helper:

```bash
.\setup.ps1 install
.\setup.ps1 run
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
- Instalación y uso sin clonar (paquete publicado): [docs/INSTALACION_SIN_CLONAR.md](docs/INSTALACION_SIN_CLONAR.md)

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

