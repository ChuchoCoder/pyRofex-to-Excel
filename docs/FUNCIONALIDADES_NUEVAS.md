# Funcionalidades nuevas de pyRofex-To-Excel

Este documento resume las mejoras recientes de la app para operación diaria.

## 1) Bootstrap de primer arranque

Cuando ejecutás la app por primera vez:
- Si faltan credenciales (`PYROFEX_USER`, `PYROFEX_PASSWORD`, `PYROFEX_ACCOUNT`), se solicitan por consola.
- Los valores se persisten en `.env` automáticamente.
- Se refrescan constantes de configuración en runtime para evitar reinicio manual.

Impacto operativo:
- Onboarding más rápido para usuarios nuevos.
- Menos errores de configuración inicial.

## 2) Creación automática del workbook y hojas base

Si el archivo configurado no existe, la app puede crear workbook nuevo y bootstrappear estructura mínima.

Hojas objetivo:
- `Tickers`
- `MarketData`
- `Trades`
- `Formulas`

Además:
- Se aplica orden canónico de tabs al crearse estructura.
- Se crean headers mínimos para operación inmediata.

## 3) Hoja `MarketData` mejorada para cauciones

Se asegura layout lateral de cauciones (Q:Z):
- headers
- columna de días/plazos
- fórmula de promedio TLR con tolerancia regional (`;` o `,`)

Impacto operativo:
- Menos setup manual en planilla.
- Compatibilidad con distintas configuraciones regionales de Excel.

## 4) Formato visual inicial (solo bootstrap)

El formateo pesado se aplica en creación inicial para no degradar performance ni pisar cambios del usuario en ejecuciones posteriores.

Incluye:
- tipografía Calibri 9
- dark theme
- formatos numéricos (% / fecha / hora / enteros / decimales)
- anchos de columnas

## 5) Hoja `Formulas` (antes `Ejemplos`)

Se crea en workbook nuevo con:
- Caso de uso
- Fórmula activa
- Fórmula texto para copy/paste
- Nota explicativa

Parámetros editables:
- `G2`: símbolo principal
- `G3`: símbolo alternativo

Contenidos incluidos:
- precio, puntas y tamaños
- métricas de caución (tasa/plazo/monto cercano)
- métricas trader: spread, bps, mid, microprice, desbalance, notionals, slippage, chequeos de consistencia

## 6) Auto-poblado de `Tickers`

Si `Tickers` está vacío en primer arranque, se intenta poblar desde `data/cache/instruments_cache.json` con reglas de negocio por categoría.

Impacto operativo:
- permite arrancar más rápido sin cargar todo manualmente.

## 7) Trades: sincronización periódica y realtime

La hoja `Trades` puede operar en dos modos:
- Periódico REST (`TRADES_REALTIME_ENABLED=false`)
- Realtime WebSocket (`TRADES_REALTIME_ENABLED=true`)

Configuración clave:
- `TRADES_SYNC_ENABLED`
- `TRADES_SYNC_INTERVAL_SECONDS`
- `TRADES_BATCH_SIZE`

## 8) Optimización de escritura a Excel

La app evita actualizar Excel cuando no hay market data nueva.

Impacto operativo:
- menor consumo de CPU/COM
- mejor respuesta en sesiones largas
- menos flicker visual

## 9) Cambios de nomenclatura por defecto

- Hoja de precios por defecto: `MarketData` (en lugar de `HomeBroker`)
- Archivo por defecto de ejemplo: `pyRofex-Market-Data.xlsb`

---

Para el paso a paso de uso inicial, ver [README.md](../README.md).
Para publicación como paquete pip, ver [PUBLICACION_PYPI.md](PUBLICACION_PYPI.md).
