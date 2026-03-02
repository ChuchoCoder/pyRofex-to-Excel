# pyRofex-to-Excel

[![CI](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml)
[![Package Release](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml)

Aplicación Python para obtener datos de mercado en tiempo real desde pyRofex y volcarlos a Excel.

---

> **¿Quién sos?**
>
> - **Usuario final** — solo querés usar la app → [Modo Usuario](#-modo-usuario--instalación-desde-pypi)
> - **Desarrollador** — querés modificar o contribuir al código → [Modo Desarrollador](#️-modo-desarrollador--repositorio-clonado)

---

## 📌 Qué hace la app

- Suscribe instrumentos de `Tickers` contra pyRofex.
- Actualiza cotizaciones en `MarketData` (incluyendo cauciones).
- Sincroniza operaciones en `Trades` (modo periódico y opcional realtime).
- Evita escrituras innecesarias a Excel cuando no hay cambios (mejor performance).

---

## 👤 Modo Usuario — Instalación desde PyPI

> **No necesitás clonar el repositorio ni saber de Python.**
> Instalás el paquete publicado y lo ejecutás directamente.

### Requisitos

- Windows + Microsoft Excel instalado
- Python 3.9 o superior
- Credenciales de acceso a Matriz (Primary API) provistas por tu Broker/ALyC

### 1. Instalar

Sin entorno virtual (más rápido):

```bash
python -m pip install --user pyrofex-to-excel
```

Con entorno virtual (recomendado para aislar dependencias):

```bash
mkdir pyrofex-app
cd pyrofex-app
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pyrofex-to-excel
```

### 2. Ejecutar

```bash
pyrofex-to-excel
```

En el primer inicio la app pedirá los datos de conexión de forma interactiva:

```text
Usuario (Matriz): 20123456
Contraseña (Matriz): ********
Nº Cuenta (Matriz): 15026
Broker (ejemplo: ingresá "cocos" si usás api.cocos.xoms.com.ar) [cocos]:
Nombre del archivo Excel (sin extensión) [pyRofex-Market-Data]:
```

Qué sucede automáticamente:
- Las credenciales y configuración se guardan en `.env` (no se vuelven a pedir).
- Si la conexión a Matriz falla, la app corta sin crear ningún archivo.
- Si la conexión es exitosa, crea el workbook `.xlsx` y las hojas base: `Tickers`, `MarketData`, `Trades`, `Formulas`.
- Carga instrumentos disponibles desde pyRofex en la hoja `Tickers`.

### 3. Verificar que funciona

- Abrí el workbook generado.
- Confirmá que existen las hojas `Tickers`, `MarketData`, `Trades` y `Formulas`.
- En `MarketData` deberían empezar a actualizarse precios.

### Reconfigurar credenciales

Si necesitás cambiar usuario, contraseña u otro dato:

```bash
pyrofex-to-excel --reconfigure
```

### Ver versión instalada

```bash
pyrofex-to-excel --version
```

Para guía completa de actualización y desinstalación, ver [docs/INSTALACION_SIN_CLONAR.md](docs/INSTALACION_SIN_CLONAR.md).

---

## 🛠️ Modo Desarrollador — Repositorio clonado

> **Para quienes quieren modificar el código, agregar funcionalidades o contribuir al proyecto.**
> Requiere clonar el repo e instalar en modo editable.

### 1. Clonar e instalar

```bash
git clone https://github.com/ChuchoCoder/pyRofex-to-Excel.git
cd pyRofex-to-Excel
python -m venv .venv
.venv\Scripts\activate
pip install -e . --force-reinstall
```

### 2. Ejecutar

```bash
python -m pyRofex_To_Excel
```

O con el script helper:

```bash
.\setup.ps1 run
```

### 3. Tests y validación

```bash
pytest
python tools/validate_system.py
python tools/validate_quickstart.py
```

### TestPyPI

TestPyPI se usa exclusivamente para pruebas de CI/CD (builds de PR y push a `main`). No está destinado a usuarios finales.

Para instalar un build de testing específico:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyrofex-to-excel
```

---

## ⚙️ Configuración avanzada (`.env`)

La app crea y gestiona `.env` automáticamente en el primer inicio. Para ajuste fino, las variables disponibles son:

```env
EXCEL_FILE=pyRofex-Market-Data.xlsx
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
PYROFEX_CONNECTION_TIMEOUT_SECONDS=20
PYROFEX_USER=REPLACE_WITH_YOUR_USERNAME
PYROFEX_PASSWORD=REPLACE_WITH_YOUR_PASSWORD
PYROFEX_ACCOUNT=REPLACE_WITH_YOUR_ACCOUNT
```

---

## 🔒 Seguridad

- Nunca subas `.env` con credenciales reales al repositorio.
- Rotá credenciales periódicamente.
- Revisá permisos de archivos sensibles en tu entorno local.

---

## 📚 Documentación

- Funcionalidades nuevas y cambios relevantes: [docs/FUNCIONALIDADES_NUEVAS.md](docs/FUNCIONALIDADES_NUEVAS.md)
- Publicación como paquete pip (PyPI/TestPyPI): [docs/PUBLICACION_PYPI.md](docs/PUBLICACION_PYPI.md)
- Instalación y uso sin clonar (paquete publicado): [docs/INSTALACION_SIN_CLONAR.md](docs/INSTALACION_SIN_CLONAR.md)
