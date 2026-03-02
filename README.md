# pyRofex-to-Excel

[![CI](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/ci.yml)
[![Package Release](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml/badge.svg)](https://github.com/ChuchoCoder/pyRofex-to-Excel/actions/workflows/package-release.yml)

Aplicación Python para obtener datos de mercado en tiempo real desde pyRofex y volcarlos a Excel.

## 🚀 Correr desde cero (paquete publicado en PyPI)

Si solo querés usar la app (sin clonar el repo), este es el camino más simple.

1. Requisitos mínimos
   - Windows + Microsoft Excel instalado
   - Python 3.9 o superior
   - Acceso a Matriz (Primary API) provisto por tu Broker/ALyC

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
- Si la autenticación/conexión a Matriz falla, la app corta la ejecución sin crear workbook ni sheets.
- Si la conexión a Matriz es exitosa y no existe workbook, crea uno nuevo (`.xlsx`) en la ruta configurada.
- Crea y prepara hojas base: `Tickers`, `MarketData`, `Trades`, `Formulas` (solo después de validar conexión).
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
PYROFEX_CONNECTION_TIMEOUT_SECONDS=20
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

## 💻 Correr aplicación

```powershell

>.\setup.ps1 run

🚀 Running pyRofex-to-Excel...
🔄 Running application
   Running: python -m pyRofex_To_Excel
2026-03-02 09:28:55,787 - pyRofex_To_Excel.main - INFO - Versión de pyRofex-to-Excel: 1.1.5
2026-03-02 09:28:55,787 - pyRofex_To_Excel.main - INFO - Validando configuraciones...
0m)
2026-03-02 09:28:55,788 - pyRofex_To_Excel.market_data.instrument_cache - INFO - Usando caché multi-nivel: Memoria → Archivo → API
2026-03-02 09:28:55,788 - pyRofex_To_Excel.market_data.api_client - INFO - Inicializando sesión pyRofex (timeout de conexión: 20.0s)
2026-03-02 09:28:57,189 - pyRofex_To_Excel.market_data.api_client - INFO - pyRofex inicializado con entorno: LIVE
2026-03-02 09:28:57,189 - pyRofex_To_Excel.market_data.api_client - INFO - Autenticación con Matriz verificada correctamente (sin probe REST adicional)
2026-03-02 09:28:57,189 - pyRofex_To_Excel.main - INFO - Pre-cargando instrumentos disponibles desde pyRofex...
2026-03-02 09:28:57,244 - pyRofex_To_Excel.market_data.instrument_cache - INFO - ✗ Caché en archivo expirado (edad: 2451.8m > TTL: 30m)
2026-03-02 09:28:57,249 - pyRofex_To_Excel.market_data.api_client - INFO - Obteniendo instrumentos disponibles desde la API de pyRofex...
2026-03-02 09:29:04,479 - pyRofex_To_Excel.market_data.instrument_cache - INFO - ✓ Guardados 7227 instrumentos en caché (MEMORIA + ARCHIVO)
2026-03-02 09:29:04,481 - pyRofex_To_Excel.market_data.api_client - INFO - Obtenidos 7227 instrumentos desde la API
2026-03-02 09:29:04,482 - pyRofex_To_Excel.main - INFO - ✅ Pre-cargados 7227 instrumentos al caché
2026-03-02 09:29:04,482 - pyRofex_To_Excel.main - INFO - 📊 Caché de instrumentos: 7227 instrumentos, 1025 opciones
2026-03-02 09:29:04,482 - pyRofex_To_Excel.market_data.api_client - INFO - Manejador de datos de mercado registrado
2026-03-02 09:29:04,482 - pyRofex_To_Excel.market_data.api_client - INFO - Manejador de errores registrado
2026-03-02 09:29:04,482 - pyRofex_To_Excel.market_data.api_client - INFO - Manejador de excepciones configurado
2026-03-02 09:29:04,482 - pyRofex_To_Excel.main - INFO - ✅ Componentes de datos de mercado inicializados
2026-03-02 09:29:04,482 - pyRofex_To_Excel.main - INFO - Inicializando componentes de Excel...
2026-03-02 09:29:04,482 - pyRofex_To_Excel.excel.workbook_manager - INFO - Archivo de Excel no encontrado. Creando uno nuevo: pyRofex-Market-Data.xlsx
2026-03-02 09:29:08,131 - pyRofex_To_Excel.excel.workbook_manager - INFO - Conectado al libro de Excel: pyRofex-Market-Data.xlsx
2026-03-02 09:29:08,237 - pyRofex_To_Excel.excel.workbook_manager - INFO - Hoja creada automáticamente: MarketData
2026-03-02 09:29:08,258 - pyRofex_To_Excel.excel.workbook_manager - INFO - Hoja creada automáticamente: Tickers
2026-03-02 09:29:09,223 - pyRofex_To_Excel.excel.workbook_manager - INFO - Hoja Formulas creada con fórmulas de referencia a MarketData
2026-03-02 09:29:09,712 - pyRofex_To_Excel.excel.workbook_manager - INFO - Hoja Tickers poblada automáticamente desde cache de instrumentos
2026-03-02 09:29:09,744 - pyRofex_To_Excel.excel.workbook_manager - INFO - Estructura mínima de hojas verificada/creada correctamente
2026-03-02 09:29:09,749 - pyRofex_To_Excel.main - INFO - ✅ Componentes de Excel inicializados
2026-03-02 09:29:09,749 - pyRofex_To_Excel.main - INFO - Cargando símbolos desde Excel...
2026-03-02 09:29:09,749 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargando todos los símbolos desde Excel
2026-03-02 09:29:09,776 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 345 símbolos de opciones
2026-03-02 09:29:09,800 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 30 símbolos de acciones
2026-03-02 09:29:09,828 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 90 símbolos de bonos
2026-03-02 09:29:09,870 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 20 símbolos de CEDEARs
2026-03-02 09:29:09,894 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 20 símbolos de letras
2026-03-02 09:29:09,915 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 20 símbolos de ONs
2026-03-02 09:29:09,944 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 12 símbolos de Panel General
2026-03-02 09:29:09,981 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargados 24 símbolos de Futuros
2026-03-02 09:29:09,982 - pyRofex_To_Excel.excel.symbol_loader - INFO - Creados 32 símbolos de cauciones
2026-03-02 09:29:09,982 - pyRofex_To_Excel.excel.symbol_loader - INFO - Cargado un total de 593 símbolos en todos los tipos de instrumentos
2026-03-02 09:29:09,983 - pyRofex_To_Excel.main - INFO - Cargados 24 símbolos de futuros desde Excel
2026-03-02 09:29:09,983 - pyRofex_To_Excel.main - INFO - Resumen de carga de símbolos:
2026-03-02 09:29:09,983 - pyRofex_To_Excel.main - INFO -   - options: 345 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - acciones: 30 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - bonos: 90 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - cedears: 20 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - letras: 20 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - ons: 20 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - panel_general: 12 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - futuros: 24 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO -   - cauciones: 32 símbolos
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO - ✅ Total de símbolos cargados: 561
2026-03-02 09:29:09,984 - pyRofex_To_Excel.main - INFO - Validando símbolos contra instrumentos disponibles en pyRofex...
2026-03-02 09:29:09,984 - pyRofex_To_Excel.market_data.api_client - INFO - Validación de símbolos: 345 válidos, 0 inválidos de 345 totales
2026-03-02 09:29:09,985 - pyRofex_To_Excel.market_data.api_client - INFO - Validación de símbolos: 216 válidos, 0 inválidos de 216 totales
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - INFO - Valores: 216/216 válidos
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - INFO -   - Futuros: 24/24 válidos
2026-03-02 09:29:09,985 - pyRofex_To_Excel.market_data.api_client - WARNING - Se encontraron 11 símbolos inválidos: ['MERV - XMEV - PESOS - 5D', 'MERV - XMEV - PESOS - 6D', 'MERV - XMEV - PESOS - 12D', 'MERV - XMEV - PESOS - 13D', 'MERV - XMEV - PESOS - 19D']...
2026-03-02 09:29:09,985 - pyRofex_To_Excel.market_data.api_client - INFO - Validación de símbolos: 21 válidos, 11 inválidos de 32 totales
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING - 11 cauciones inválidas encontradas en Excel:
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 5D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 6D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 12D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 13D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 19D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 20D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 22D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 26D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 27D
2026-03-02 09:29:09,985 - pyRofex_To_Excel.main - WARNING -     - MERV - XMEV - PESOS - 31D
2026-03-02 09:29:09,986 - pyRofex_To_Excel.main - WARNING -     ... y 1 más
2026-03-02 09:29:09,986 - pyRofex_To_Excel.main - INFO - Cauciones: 21/32 válidas
2026-03-02 09:29:09,987 - pyRofex_To_Excel.main - WARNING - Total: 11 símbolos inválidos removidos del Excel
2026-03-02 09:29:09,987 - pyRofex_To_Excel.main - INFO - ✅ 582 símbolos válidos listos para suscripción
2026-03-02 09:29:09,987 - pyRofex_To_Excel.main - INFO - Trades sync está habilitado, inicializando componentes...
2026-03-02 09:29:09,987 - pyRofex_To_Excel.main - INFO - Inicializando componentes de Trades...
2026-03-02 09:29:10,107 - pyRofex_To_Excel.main - INFO - 🔄 Sincronizando órdenes ejecutadas existentes desde la API...
2026-03-02 09:29:10,460 - pyRofex_To_Excel.main - INFO - ⏱️  Real-time trades updates DISABLED - using periodic sync every 20s
2026-03-02 09:29:10,460 - pyRofex_To_Excel.main - INFO - ✅ Componentes de Trades inicializados correctamente
2026-03-02 09:29:10,460 - pyRofex_To_Excel.main - INFO - ✅ Inicialización de la aplicación completada exitosamente
2026-03-02 09:29:10,461 - pyRofex_To_Excel.main - INFO - Iniciando suscripción a datos de mercado...
2026-03-02 09:29:11,795 - websocket - INFO - Websocket connected
2026-03-02 09:29:12,463 - pyRofex_To_Excel.market_data.api_client - INFO - Suscripto a datos de mercado para 345 símbolos
2026-03-02 09:29:12,463 - pyRofex_To_Excel.main - INFO - ✅ Suscripto a 345 opciones
2026-03-02 09:29:12,464 - pyRofex_To_Excel.market_data.api_client - INFO - Suscripto a datos de mercado para 216 símbolos
2026-03-02 09:29:12,464 - pyRofex_To_Excel.main - INFO - ✅ Suscripto a 216 valores
2026-03-02 09:29:12,464 - pyRofex_To_Excel.main - INFO -   - Incluye 24 futuros
2026-03-02 09:29:12,464 - pyRofex_To_Excel.market_data.api_client - INFO - Suscripto a datos de mercado para 21 símbolos
2026-03-02 09:29:12,464 - pyRofex_To_Excel.main - INFO - ✅ Suscripto a 21 cauciones
2026-03-02 09:29:12,464 - connection - INFO - [2026-03-02 09:29:12] Suscripción a Datos de Mercado: Iniciado exitosamente
2026-03-02 09:29:12,464 - pyRofex_To_Excel.main - INFO - ✅ Aplicación ejecutándose - streaming de datos de mercado iniciado      
2026-03-02 09:29:12,464 - pyRofex_To_Excel.main - INFO - Esperando que los datos de mercado iniciales se pueblen...
2026-03-02 09:29:14,465 - pyRofex_To_Excel.main - INFO - ✅ Iniciando bucle principal - todos los logs se mostrarán en UNA línea actualizable
2026-03-02 09:29:14,466 - pyRofex_To_Excel.main - INFO - 📊 Primera actualización de Excel - inicializando
2026-03-02 09:29:14,569 - pyRofex_To_Excel.excel.sheet_operations - INFO - 📋 Caché de filas construido: 0 símbolos desde Excel
2026-03-02 09:29:14,569 - pyRofex_To_Excel.excel.sheet_operations - INFO - ➕ Auto-poblando 561 símbolos nuevos en la hoja Prices...
[09:29:37] 📊 Ciclo 8 | 📡 WS: 582/582 msgs (0 err) | 📈 Excel: 1 acts. | 📝 0 orders

```