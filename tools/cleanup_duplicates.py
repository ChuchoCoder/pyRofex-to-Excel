"""
Script para limpiar símbolos duplicados en la hoja de Excel.

Este script se conecta al archivo Excel EPGB-ChuchoTrader.xlsb y elimina
cualquier fila duplicada en la hoja Prices.

Uso:
    python tools/cleanup_duplicates.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(src_path))

from epgb_options.config import EXCEL_FILE, EXCEL_PATH, EXCEL_SHEET_PRICES
from epgb_options.excel import SheetOperations, WorkbookManager
from epgb_options.market_data import pyRofexClient
from epgb_options.utils import get_logger, setup_logging

logger = get_logger(__name__)


def cleanup_duplicates():
    """Limpia símbolos duplicados del archivo Excel."""
    
    # Setup logging
    setup_logging()
    
    logger.info("="*70)
    logger.info("LIMPIEZA DE SÍMBOLOS DUPLICADOS")
    logger.info("="*70)
    
    try:
        # Initialize API client to get instrument cache
        logger.info("Inicializando cliente API para obtener caché de instrumentos...")
        api_client = pyRofexClient()
        if not api_client.initialize():
            logger.error("No se pudo inicializar el cliente API")
            return False
        
        # Pre-load instruments for option detection
        logger.info("Cargando instrumentos disponibles...")
        api_client.fetch_available_instruments()
        
        # Connect to Excel workbook
        logger.info(f"Conectando a Excel: {EXCEL_FILE}")
        workbook_manager = WorkbookManager(EXCEL_FILE, EXCEL_PATH)
        if not workbook_manager.connect():
            logger.error("No se pudo conectar al archivo Excel")
            return False
        
        # Initialize sheet operations with instrument cache
        logger.info("Inicializando operaciones de hoja...")
        sheet_ops = SheetOperations(workbook_manager.workbook, api_client.instrument_cache)
        
        # Cleanup duplicates in Prices sheet
        logger.info(f"Buscando duplicados en la hoja '{EXCEL_SHEET_PRICES}'...")
        duplicates_removed = sheet_ops.cleanup_duplicate_symbols(EXCEL_SHEET_PRICES)
        
        # Summary
        logger.info("")
        logger.info("="*70)
        logger.info("RESUMEN")
        logger.info("="*70)
        logger.info(f"Filas duplicadas eliminadas: {duplicates_removed}")
        logger.info("="*70)
        
        # Close Excel connection
        workbook_manager.disconnect()
        api_client.close_connection()
        
        logger.info("✅ Proceso completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = cleanup_duplicates()
    sys.exit(0 if success else 1)
