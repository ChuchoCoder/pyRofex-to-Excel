"""
Administrador de libros de Excel para EPGB Options.

Este módulo maneja las conexiones y administración de libros de Excel.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import xlwings as xw

from ..utils.helpers import clean_symbol_for_display
from ..utils.logging import get_logger

logger = get_logger(__name__)


class WorkbookManager:
    """Administra conexiones y operaciones de libros de Excel."""
    
    def __init__(self, excel_file: str, excel_path: str = "./"):
        """
        Inicializar administrador de libros.
        
        Args:
            excel_file: Nombre del archivo de Excel
            excel_path: Ruta al archivo de Excel
        """
        self.excel_file = excel_file
        self.excel_path = excel_path
        self.workbook = None
        self._is_connected = False
    
    def connect(self, create_if_missing: bool = False) -> bool:
        """
        Conectar al libro de Excel.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Construir ruta completa
            full_path = Path(self.excel_path) / self.excel_file
            
            # Verificar si el archivo existe
            if not full_path.exists():
                if not create_if_missing:
                    logger.error(f"Archivo de Excel no encontrado: {full_path}")
                    return False

                logger.info(f"Archivo de Excel no encontrado. Creando uno nuevo: {full_path}")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                new_workbook = xw.Book()
                new_workbook.save(str(full_path))
                new_workbook.close()
            
            # Conectar al libro
            self.workbook = xw.Book(str(full_path))
            self._is_connected = True
            
            logger.info(f"Conectado al libro de Excel: {self.excel_file}")
            return True
            
        except Exception as e:
            logger.error(f"Fallo al conectar al libro de Excel: {e}")
            self._is_connected = False
            return False

    def ensure_sheet(self, sheet_name: str) -> Optional[xw.Sheet]:
        """
        Obtener o crear una hoja por nombre.

        Args:
            sheet_name: Nombre de la hoja

        Returns:
            xlwings.Sheet o None si falla
        """
        if not self.is_connected():
            logger.error("No conectado al libro")
            return None

        try:
            return self.workbook.sheets[sheet_name]
        except Exception:
            try:
                sheet = self.workbook.sheets.add(sheet_name)
                logger.info(f"Hoja creada automáticamente: {sheet_name}")
                return sheet
            except Exception as e:
                logger.error(f"No se pudo crear la hoja '{sheet_name}': {e}")
                return None

    def enforce_sheet_order(self, preferred_order: List[str]):
        """
        Reordenar hojas para que las existentes en preferred_order queden al inicio
        en ese orden exacto.
        """
        if not self.is_connected():
            return

        try:
            for sheet_name in reversed(preferred_order):
                try:
                    sheet = self.workbook.sheets[sheet_name]
                    first_sheet = self.workbook.sheets[0]
                    sheet.api.Move(Before=first_sheet.api)
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"No se pudo aplicar orden de hojas: {e}")

    def bootstrap_required_sheets(self, prices_sheet_name: str, tickers_sheet_name: str,
                                  trades_sheet_name: str = 'Trades') -> bool:
        """
        Asegura que existan hojas requeridas y plantilla mínima para primer arranque.

        Args:
            prices_sheet_name: Nombre de hoja de precios
            tickers_sheet_name: Nombre de hoja de tickers

        Returns:
            bool: True si el bootstrap de hojas fue exitoso
        """
        if not self.is_connected():
            logger.error("No conectado al libro")
            return False

        # Detect worksheet existence state (before ensure/create)
        prices_preexisting = any(s.name == prices_sheet_name for s in self.workbook.sheets)
        tickers_preexisting = any(s.name == tickers_sheet_name for s in self.workbook.sheets)
        is_new_excel = (not prices_preexisting) and (not tickers_preexisting)

        prices_sheet = self.ensure_sheet(prices_sheet_name)
        tickers_sheet = self.ensure_sheet(tickers_sheet_name)

        if not prices_sheet or not tickers_sheet:
            return False

        try:
            # Prices headers mínimos A:O
            prices_headers = [
                'symbol', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'change',
                'open', 'high', 'low', 'previous_close', 'turnover', 'volume',
                'operations', 'datetime'
            ]
            existing_prices_header = prices_sheet.range('A1').value
            if not existing_prices_header:
                prices_sheet.range('A1:O1').value = prices_headers
                prices_sheet.range('A1:O1').font.bold = True

            # Tabla de cauciones (lateral derecho): headers + columnas de días/plazo
            cauciones_headers = [
                'Promedio T.',
                'Plazo',
                'Vencimiento',
                'Tasa',
                'Monto $',
                'Monto Tomador',
                'Tasa Tomadora',
                'Tasa Colocadora',
                'Monto Colocador',
                'Prom. TLR',
            ]
            current_cauciones_headers = prices_sheet.range('Q1:Z1').value
            if not current_cauciones_headers or current_cauciones_headers[0] != 'Promedio T.':
                prices_sheet.range('Q1:Z1').value = cauciones_headers
                prices_sheet.range('Q1:Z1').font.bold = True

            day_values = [[i] for i in range(1, 34)]
            plazo_values = [[f"{i} día" if i == 1 else f"{i} días"] for i in range(1, 34)]

            existing_days = prices_sheet.range('Q2:Q34').value
            existing_plazos = prices_sheet.range('R2:R34').value

            # Si no hay datos previos, sembrar base completa
            if not existing_days:
                prices_sheet.range('Q2:Q34').value = day_values
            if not existing_plazos:
                prices_sheet.range('R2:R34').value = plazo_values

            # Promedio TLR en Z2 (si está vacío)
            existing_prom_tlr = prices_sheet.range('Z2').value
            if existing_prom_tlr is None or str(existing_prom_tlr).strip() == '':
                formula_set = False
                for formula_candidate in (
                    '=IFERROR(AVERAGEIF(T2:T8,"<>0"),0)',
                    '=IFERROR(AVERAGEIF(T2:T8;"<>0");0)',
                ):
                    try:
                        prices_sheet.range('Z2').formula = formula_candidate
                        formula_set = True
                        break
                    except Exception:
                        continue

                if not formula_set:
                    logger.warning("No se pudo establecer fórmula de Prom. TLR en Z2")

            # Formato visual inicial SOLO cuando Tickers se crea por primera vez
            if not tickers_preexisting:
                try:
                    header_bg = (26, 26, 26)
                    header_fg = (255, 255, 255)
                    body_bg = (0, 0, 0)
                    cyan_fg = (104, 173, 255)
                    yellow_fg = (243, 224, 116)
                    separator_bg = (96, 96, 96)

                    prices_sheet.range('A1:Z2000').color = body_bg
                    prices_sheet.range('A2:O2000').font.color = cyan_fg
                    prices_sheet.range('Q2:Z2000').font.color = header_fg

                    # Global font
                    prices_sheet.range('A:Z').font.name = 'Calibri'
                    prices_sheet.range('A:Z').font.size = 9

                    prices_sheet.range('P:P').color = separator_bg
                    prices_sheet.range('P:P').column_width = 2.5

                    prices_sheet.range('A1:O1').color = header_bg
                    prices_sheet.range('A1:O1').font.color = header_fg
                    prices_sheet.range('A1:O1').font.bold = True

                    prices_sheet.range('Q1:Z1').color = header_bg
                    prices_sheet.range('Q1:Z1').font.color = header_fg
                    prices_sheet.range('Q1:Z1').font.bold = True

                    prices_sheet.range('A1:Z1').font.name = 'Calibri'
                    prices_sheet.range('A1:Z1').font.size = 9

                    # Per-column font colors
                    prices_sheet.range('A:A').font.color = header_fg
                    prices_sheet.range('B:B').font.color = cyan_fg
                    prices_sheet.range('C:D').font.color = yellow_fg
                    prices_sheet.range('E:E').font.color = cyan_fg
                    prices_sheet.range('F:F').font.color = yellow_fg
                    prices_sheet.range('H:K').font.color = cyan_fg
                    prices_sheet.range('L:N').font.color = cyan_fg
                    prices_sheet.range('O:O').font.color = header_fg

                    prices_sheet.range('Q:S').font.color = header_fg
                    prices_sheet.range('U:V').font.color = header_fg
                    prices_sheet.range('Y:Y').font.color = header_fg

                    percent_format = '[Green]0.00%;[Red]-0.00%;0.00%'
                    prices_sheet.range('G:G').number_format = percent_format
                    prices_sheet.range('T:T').number_format = percent_format
                    prices_sheet.range('W:W').number_format = percent_format
                    prices_sheet.range('X:X').number_format = percent_format
                    prices_sheet.range('Z:Z').number_format = percent_format

                    pct_green = (0, 255, 170)
                    prices_sheet.range('G:G').font.color = pct_green
                    prices_sheet.range('T:T').font.color = pct_green
                    prices_sheet.range('W:X').font.color = pct_green

                    prices_sheet.range('B:B').number_format = '#,##0'
                    prices_sheet.range('E:E').number_format = '#,##0'
                    prices_sheet.range('N:N').number_format = '#,##0'
                    prices_sheet.range('Q:Q').number_format = '#,##0'

                    prices_sheet.range('C:C').number_format = '0.000'
                    prices_sheet.range('D:D').number_format = '0.000'
                    prices_sheet.range('F:F').number_format = '0.000'
                    prices_sheet.range('H:H').number_format = '0.000'
                    prices_sheet.range('I:I').number_format = '0.000'
                    prices_sheet.range('J:J').number_format = '0.000'
                    prices_sheet.range('K:K').number_format = '0.000'

                    prices_sheet.range('L:L').number_format = '#,##0'
                    prices_sheet.range('M:M').number_format = '#,##0'
                    prices_sheet.range('U:U').number_format = '#,##0'
                    prices_sheet.range('V:V').number_format = '#,##0'
                    prices_sheet.range('Y:Y').number_format = '#,##0'

                    prices_sheet.range('O:O').number_format = 'hh:mm:ss'
                    prices_sheet.range('S:S').number_format = 'd/m/yyyy'

                    col_widths = {
                        'A': 14, 'B': 9, 'C': 10, 'D': 10, 'E': 9, 'F': 9,
                        'G': 9, 'H': 9, 'I': 9, 'J': 9, 'K': 12, 'L': 13,
                        'M': 12, 'N': 11, 'O': 10,
                        'Q': 8, 'R': 9, 'S': 12, 'T': 9, 'U': 14,
                        'V': 13, 'W': 12, 'X': 13, 'Y': 13, 'Z': 10,
                    }
                    for col, width in col_widths.items():
                        prices_sheet.range(f'{col}:{col}').column_width = width

                    prices_sheet.range('1:1').row_height = 20
                    prices_sheet.range('2:400').row_height = 18

                    prices_sheet.range('A:Z').api.HorizontalAlignment = -4108
                    prices_sheet.range('A:A').api.HorizontalAlignment = -4131
                    prices_sheet.range('R:R').api.HorizontalAlignment = -4131

                    for table_range in (prices_sheet.range('A1:O2000'), prices_sheet.range('Q1:Z2000')):
                        table_range.api.Borders.LineStyle = 1
                        table_range.api.Borders.Weight = 1

                    try:
                        prices_sheet.range('A2').select()
                        prices_sheet.book.app.api.ActiveWindow.FreezePanes = True
                    except Exception:
                        pass
                except Exception as style_error:
                    logger.warning(f"No se pudo aplicar formato visual inicial: {style_error}")

            # Tickers headers mínimos en columnas usadas por SymbolLoader
            tickers_headers = {
                'A1': 'Opciones',
                'C1': 'Acciones',
                'E1': 'Bonos',
                'G1': 'CEDEARs',
                'I1': 'Letras',
                'K1': 'ONs',
                'M1': 'Panel General',
                'O1': 'Futuros',
            }
            for cell, header in tickers_headers.items():
                if not tickers_sheet.range(cell).value:
                    tickers_sheet.range(cell).value = header

            tickers_sheet.range('A1:O1').font.bold = True

            # Hoja de fórmulas: crear SOLO para Excel nuevo y dejar fórmulas listas para copiar/pegar
            if is_new_excel:
                self._create_examples_sheet(prices_sheet_name)

            # Enforce canonical sheet order ONLY if some sheet was created in this bootstrap
            if (not prices_preexisting) or (not tickers_preexisting):
                self.enforce_sheet_order([tickers_sheet_name, prices_sheet_name, trades_sheet_name, 'Formulas'])

            # Poblar Tickers automáticamente sólo en primer arranque (cuando está vacío)
            if self._is_tickers_data_empty(tickers_sheet):
                seeded = self._seed_tickers_from_instruments_cache(tickers_sheet)
                if seeded:
                    logger.info("Hoja Tickers poblada automáticamente desde cache de instrumentos")
                else:
                    logger.warning("No se pudo poblar Tickers desde cache; se mantiene plantilla mínima")

            self.workbook.save()
            logger.info("Estructura mínima de hojas verificada/creada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar hojas requeridas: {e}")
            return False

    def _create_examples_sheet(self, prices_sheet_name: str) -> None:
        """Crear hoja Formulas con fórmulas de referencia a MarketData para uso manual."""
        examples_sheet_name = 'Formulas'

        if any(s.name == examples_sheet_name for s in self.workbook.sheets):
            return

        try:
            examples_sheet = self.workbook.sheets.add(examples_sheet_name)
        except Exception as e:
            logger.warning(f"No se pudo crear hoja {examples_sheet_name}: {e}")
            return

        try:
            headers = ['Caso de uso', 'Fórmula (activa)', 'Fórmula para copiar/pegar', 'Nota']
            examples_sheet.range('A1:D1').value = headers
            examples_sheet.range('A1:D1').font.bold = True

            # Parámetros editables para reutilizar fórmulas con otros símbolos
            examples_sheet.range('F1:G1').value = ['Parámetro', 'Valor']
            examples_sheet.range('F1:G1').font.bold = True
            examples_sheet.range('F2').value = 'Símbolo principal'
            examples_sheet.range('G2').value = 'GGAL - 24hs'
            examples_sheet.range('F3').value = 'Símbolo alternativo'
            examples_sheet.range('G3').value = 'GGAL - CI'

            symbol_main_ref = '$G$2'
            symbol_alt_ref = '$G$3'

            examples_data = [
                [
                    'Último precio (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    'Busca símbolo de G2 en columna A y devuelve last (F).',
                ],
                [
                    'Último precio (símbolo alternativo)',
                    f'=IFERROR(VLOOKUP({symbol_alt_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_alt_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    'Misma lógica para símbolo en G3 (ej. CI).',
                ],
                [
                    'Bid size (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0),0)',
                    'Devuelve cantidad a la compra (bid_size, columna B).',
                ],
                [
                    'Bid price (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),0)',
                    'Devuelve precio bid (columna C).',
                ],
                [
                    'Ask price (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0),0)',
                    'Devuelve precio ask (columna D).',
                ],
                [
                    'Ask size (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0),0)',
                    'Devuelve cantidad a la venta (ask_size, columna E).',
                ],
                [
                    'Tasa caución más cercana disponible',
                    f'=IFERROR(INDEX({prices_sheet_name}!$T$2:$T$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),0)',
                    f'=IFERROR(INDEX({prices_sheet_name}!$T$2:$T$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),0)',
                    'Toma la primera tasa no cero desde 1 día en adelante (útil feriados/fin de semana).',
                ],
                [
                    'Plazo de caución usado',
                    f'=IFERROR(INDEX({prices_sheet_name}!$Q$2:$Q$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),"")',
                    f'=IFERROR(INDEX({prices_sheet_name}!$Q$2:$Q$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),"")',
                    'Devuelve el día/plazo (Q) correspondiente a la tasa encontrada.',
                ],
                [
                    'Monto caución para plazo cercano',
                    f'=IFERROR(INDEX({prices_sheet_name}!$U$2:$U$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),0)',
                    f'=IFERROR(INDEX({prices_sheet_name}!$U$2:$U$34,MATCH(TRUE,INDEX({prices_sheet_name}!$T$2:$T$34<>0,0),0)),0)',
                    'Trae el monto (U) del mismo plazo de tasa vigente.',
                ],
                [
                    'Variación % (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$G$2000,7,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$G$2000,7,0),0)',
                    'Devuelve change % (columna G).',
                ],
                [
                    'Spread absoluto (símbolo principal)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),0)',
                    'Mide apertura de puntas: ask - bid.',
                ],
                [
                    'Spread relativo (bps) símbolo principal',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)/VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)-1)*10000,0)',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)/VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)-1)*10000,0)',
                    'Spread en basis points para comparar liquidez entre activos.',
                ],
                [
                    'Precio medio (mid) símbolo principal',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0))/2,0)',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0))/2,0)',
                    'Proxy de precio justo instantáneo entre bid/ask.',
                ],
                [
                    'Microprice símbolo principal',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0))/(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0)),0)',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0))/(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0)),0)',
                    'Mid ponderado por profundidad de puntas (sesgo direccional corto plazo).',
                ],
                [
                    'Desbalance de libro símbolo principal',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0))/(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0)),0)',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0))/(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0)+VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0)),0)',
                    'Rango [-1,1]. Positivo = más presión compradora en punta.',
                ],
                [
                    'Notional bid en punta símbolo principal',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$B$2000,2,0),0)',
                    'Capital demandado en la mejor compra (precio x cantidad).',
                ],
                [
                    'Notional ask en punta símbolo principal',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)*VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$E$2000,5,0),0)',
                    'Capital ofertado en la mejor venta (precio x cantidad).',
                ],
                [
                    'Slippage compra estimado (bps) símbolo principal',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)/VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)-1)*10000,0)',
                    f'=IFERROR((VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)/VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)-1)*10000,0)',
                    'Costo inmediato de comprar en ask versus último precio operado.',
                ],
                [
                    'Brecha alternativo vs principal (last)',
                    f'=IFERROR(VLOOKUP({symbol_alt_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    f'=IFERROR(VLOOKUP({symbol_alt_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)-VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0),0)',
                    'Diferencial entre G3 y G2 (útil para comparar plazos/settlement).',
                ],
                [
                    'Chequeo de consistencia de puntas (símbolo principal)',
                    f'=IFERROR(IF(AND(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)>=VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)<=VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)),1,0),0)',
                    f'=IFERROR(IF(AND(VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)>=VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$C$2000,3,0),VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$F$2000,6,0)<=VLOOKUP({symbol_main_ref},{prices_sheet_name}!$A$2:$D$2000,4,0)),1,0),0)',
                    '1 si el último cae dentro del spread; 0 si hay desalineación a revisar.',
                ],
            ]

            start_row = 2
            end_row = start_row + len(examples_data) - 1

            for i, row in enumerate(examples_data):
                row_num = start_row + i
                examples_sheet.range(f'A{row_num}').value = row[0]

                formula_set = False
                for formula_candidate in (row[1], row[1].replace(',', ';')):
                    try:
                        examples_sheet.range(f'B{row_num}').formula = formula_candidate
                        formula_set = True
                        break
                    except Exception:
                        continue

                if not formula_set:
                    examples_sheet.range(f'B{row_num}').value = row[1]

                examples_sheet.range(f'C{row_num}').value = "'" + row[2]
                examples_sheet.range(f'D{row_num}').value = row[3]

            examples_sheet.range(f'A1:D{end_row}').api.Borders.LineStyle = 1
            examples_sheet.range('A:D').font.name = 'Calibri'
            examples_sheet.range('A:D').font.size = 9

            examples_sheet.range('A:A').column_width = 34
            examples_sheet.range('B:B').column_width = 52
            examples_sheet.range('C:C').column_width = 52
            examples_sheet.range('D:D').column_width = 55
            examples_sheet.range('F:F').column_width = 22
            examples_sheet.range('G:G').column_width = 24

            examples_sheet.range('A1:D1').color = (26, 26, 26)
            examples_sheet.range('A1:D1').font.color = (255, 255, 255)
            examples_sheet.range('F1:G1').color = (26, 26, 26)
            examples_sheet.range('F1:G1').font.color = (255, 255, 255)
            examples_sheet.range(f'A2:D{end_row}').color = (0, 0, 0)
            examples_sheet.range(f'A2:D{end_row}').font.color = (255, 255, 255)
            examples_sheet.range('F2:G3').color = (0, 0, 0)
            examples_sheet.range('F2:G3').font.color = (255, 255, 255)
            examples_sheet.range('G2:G3').font.color = (243, 224, 116)
            examples_sheet.range('F1:G3').api.Borders.LineStyle = 1

            examples_sheet.range(f'B2:B{end_row}').font.color = (104, 173, 255)
            examples_sheet.range(f'C2:C{end_row}').font.color = (243, 224, 116)

            logger.info("Hoja Formulas creada con fórmulas de referencia a MarketData")
        except Exception as e:
            logger.warning(f"No se pudo poblar hoja Formulas: {e}")

    def _is_tickers_data_empty(self, tickers_sheet: xw.Sheet) -> bool:
        """Verifica si la hoja Tickers no tiene datos de instrumentos cargados."""
        try:
            key_cells = ['A2', 'C2', 'E2', 'G2', 'I2', 'K2', 'M2', 'O2']
            for cell in key_cells:
                value = tickers_sheet.range(cell).value
                if value and str(value).strip():
                    return False
            return True
        except Exception as e:
            logger.warning(f"No se pudo verificar estado de Tickers: {e}")
            return False

    def _seed_tickers_from_instruments_cache(self, tickers_sheet: xw.Sheet) -> bool:
        """Poblar Tickers usando el cache de instrumentos aplicando reglas de negocio."""
        try:
            cache_path = Path(__file__).resolve().parents[3] / 'data' / 'cache' / 'instruments_cache.json'
            if not cache_path.exists():
                logger.warning(f"Archivo de cache no encontrado: {cache_path}")
                return False

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            instruments = cache_data.get('instruments', [])
            if not isinstance(instruments, list) or not instruments:
                logger.warning("Cache de instrumentos vacío o inválido")
                return False

            categories = self._build_ticker_categories(instruments)
            self._write_tickers_categories(tickers_sheet, categories)
            return True
        except Exception as e:
            logger.error(f"Error poblando Tickers desde cache: {e}")
            return False

    def _extract_symbol_and_code(self, instrument: dict) -> Optional[Tuple[str, str]]:
        """Extraer símbolo completo y código para mostrar en Tickers."""
        full_symbol = instrument.get('instrumentId', {}).get('symbol') or instrument.get('symbol')
        if not full_symbol or not isinstance(full_symbol, str):
            return None

        full_symbol = full_symbol.strip()
        if not full_symbol:
            return None

        if full_symbol.startswith('MERV - XMEV - '):
            code = clean_symbol_for_display(full_symbol, is_option=False)
        else:
            code = full_symbol

        return full_symbol, code

    def _build_ticker_categories(self, instruments: List[dict]) -> Dict[str, List[str]]:
        """
        Construir listas por categoría para Tickers.

        Reglas:
        - Orden por maturityDate y luego código
        - Al menos 20 items por columna
        - Inclusiones obligatorias por categoría según requerimiento
        """
        TARGET = 20

        rows = []
        for instrument in instruments:
            if not isinstance(instrument, dict):
                continue

            extracted = self._extract_symbol_and_code(instrument)
            if not extracted:
                continue

            full_symbol, code = extracted
            cficode = (instrument.get('cficode') or '').strip()
            maturity = (instrument.get('maturityDate') or '99999999').strip() or '99999999'

            rows.append({
                'cficode': cficode,
                'full_symbol': full_symbol,
                'code': code,
                'maturity': maturity,
            })

        # Clasificación por columnas
        acciones = [r for r in rows if r['cficode'] == 'ESXXXX' and r['full_symbol'].startswith('MERV - XMEV - ')]
        opciones = [r for r in rows if r['cficode'] in ('OCASPS', 'OPASPS') and r['full_symbol'].startswith('MERV - XMEV - ')]
        bonos = [r for r in rows if r['cficode'] == 'DBXXXX' and r['full_symbol'].startswith('MERV - XMEV - ')]
        cedears = [r for r in rows if r['cficode'] == 'EMXXXX' and r['full_symbol'].startswith('MERV - XMEV - ')]
        letras = [r for r in rows if r['cficode'] == 'DYXTXR' and r['full_symbol'].startswith('MERV - XMEV - ')]
        ons = [r for r in rows if r['cficode'] == 'DBXXFR' and r['full_symbol'].startswith('MERV - XMEV - ')]
        futuros = [r for r in rows if r['cficode'] == 'FXXXSX' and r['full_symbol'].startswith('DLR/')]

        # Panel General deriva de ESXXXX con tickers obligatorios específicos
        panel_general = [
            r for r in acciones
            if any(r['code'].startswith(prefix) for prefix in ('LEDE', 'MOLI', 'MOLA'))
        ]

        # Opciones: incluir todas GGAL (GFGC y GFGV)
        opciones = [
            r for r in opciones
            if any(r['code'].startswith(prefix) for prefix in ('GFGC', 'GFGV'))
        ]

        # Acciones obligatorias: GGAL, YPF, TXAR, ALUAR, BYMA en 24hs y CI
        acciones_required_pairs = [
            ('GGAL', '24hs'), ('GGAL', 'CI'),
            ('YPF', '24hs'), ('YPF', 'CI'),
            ('TXAR', '24hs'), ('TXAR', 'CI'),
            ('ALUA', '24hs'), ('ALUA', 'CI'),
            ('BYMA', '24hs'), ('BYMA', 'CI'),
        ]

        # Bonos obligatorios: Axxx y Gxxx
        bonos = [
            r for r in bonos
            if r['code'] and (r['code'][0] in ('A', 'G'))
        ]

        # Sort helper
        def sort_rows(items: List[dict]) -> List[dict]:
            return sorted(items, key=lambda x: (x['maturity'], x['code']))

        # Unique helper that preserves maturity for final ordering
        def unique_entries(items: List[dict], is_option: bool = False) -> List[dict]:
            result = []
            seen = set()
            for item in sort_rows(items):
                code = clean_symbol_for_display(item['full_symbol'], is_option=is_option)
                if code not in seen:
                    seen.add(code)
                    result.append({
                        'code': code,
                        'maturity': item['maturity'],
                    })
            return result

        acciones_entries = unique_entries(acciones)
        opciones_entries = unique_entries(opciones, is_option=True)
        bonos_entries = unique_entries(bonos)
        cedears_entries = unique_entries(cedears)
        letras_entries = unique_entries(letras)
        ons_entries = unique_entries(ons)
        panel_entries = unique_entries(panel_general)
        futuros_entries = unique_entries(futuros)

        def pick_minimum_with_required(
            entries: List[dict],
            target: int,
            required_predicate,
        ) -> List[str]:
            required = [entry for entry in entries if required_predicate(entry['code'])]
            required_codes = {entry['code'] for entry in required}

            selected = list(required)
            for entry in entries:
                if len(selected) >= target:
                    break
                if entry['code'] in required_codes:
                    continue
                selected.append(entry)

            selected = sorted(selected, key=lambda x: (x['maturity'], x['code']))
            return [entry['code'] for entry in selected]

        def pick_all_sorted(entries: List[dict]) -> List[str]:
            return [entry['code'] for entry in sorted(entries, key=lambda x: (x['maturity'], x['code']))]

        acciones_final = pick_minimum_with_required(
            acciones_entries,
            TARGET,
            lambda code: any(code.startswith(base) and code.endswith(settlement) for base, settlement in acciones_required_pairs),
        )

        panel_final = pick_minimum_with_required(
            panel_entries,
            TARGET,
            lambda code: any(code.startswith(base) for base in ('LEDE', 'MOLI', 'MOLA')),
        )

        # Reglas de "incluir todos"
        opciones_final = pick_all_sorted(opciones_entries)
        bonos_final = pick_all_sorted(bonos_entries)
        futuros_final = pick_all_sorted(futuros_entries)

        # Otras categorías: completar al menos target
        cedears_final = [entry['code'] for entry in cedears_entries[:TARGET]]
        letras_final = [entry['code'] for entry in letras_entries[:TARGET]]
        ons_final = [entry['code'] for entry in ons_entries[:TARGET]]

        # Backfill mínimo a 20 con string vacío sólo si mercado no provee suficientes
        def ensure_minimum(items: List[str]) -> List[str]:
            completed = list(items)
            while len(completed) < TARGET:
                completed.append('')
            return completed

        return {
            'options': ensure_minimum(opciones_final),
            'acciones': ensure_minimum(acciones_final),
            'bonos': ensure_minimum(bonos_final),
            'cedears': ensure_minimum(cedears_final),
            'letras': ensure_minimum(letras_final),
            'ons': ensure_minimum(ons_final),
            'panel_general': ensure_minimum(panel_final),
            'futuros': ensure_minimum(futuros_final),
        }

    def _write_tickers_categories(self, tickers_sheet: xw.Sheet, categories: Dict[str, List[str]]):
        """Escribir columnas de Tickers en formato plantilla (A,C,E,G,I,K,M,O)."""
        mapping = {
            'options': 'A',
            'acciones': 'C',
            'bonos': 'E',
            'cedears': 'G',
            'letras': 'I',
            'ons': 'K',
            'panel_general': 'M',
            'futuros': 'O',
        }

        for key, col in mapping.items():
            values = categories.get(key, [])
            if not values:
                continue
            vertical_values = [[v] for v in values]
            end_row = 1 + len(vertical_values)
            tickers_sheet.range(f'{col}2:{col}{end_row}').value = vertical_values
    
    def disconnect(self):
        """Desconectar del libro de Excel."""
        if self.workbook and self._is_connected:
            try:
                # Nota: No cerramos el libro ya que podría estar en uso
                # Sólo limpiamos nuestra referencia
                self.workbook = None
                self._is_connected = False
                logger.info("Desconectado del libro de Excel")
            except Exception as e:
                logger.warning(f"Error durante la desconexión: {e}")
    
    def get_sheet(self, sheet_name: str) -> Optional[xw.Sheet]:
        """
        Obtener una hoja específica del libro.
        
        Args:
            sheet_name: Nombre de la hoja a recuperar
            
        Returns:
            xlwings.Sheet or None: Objeto Sheet si se encuentra, None en caso contrario
        """
        if not self.is_connected():
            logger.error("No conectado al libro")
            return None
        
        try:
            sheet = self.workbook.sheets(sheet_name)
            logger.debug(f"Hoja recuperada: {sheet_name}")
            return sheet
        except Exception as e:
            logger.error(f"Fallo al obtener hoja '{sheet_name}': {e}")
            return None
    
    def is_connected(self) -> bool:
        """
        Verificar si está conectado al libro.
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        return self._is_connected and self.workbook is not None
    
    def get_workbook_info(self) -> dict:
        """
        Get information about the connected workbook.
        
        Returns:
            dict: Workbook information
        """
        if not self.is_connected():
            return {"connected": False}
        
        try:
            return {
                "connected": True,
                "file_name": self.excel_file,
                "file_path": self.excel_path,
                "sheet_names": [sheet.name for sheet in self.workbook.sheets]
            }
        except Exception as e:
            logger.error(f"Error getting workbook info: {e}")
            return {"connected": True, "error": str(e)}
    
    def save_workbook(self) -> bool:
        """
        Save the workbook.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.is_connected():
            logger.error("Cannot save - not connected to workbook")
            return False
        
        try:
            self.workbook.save()
            logger.info("Workbook saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save workbook: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()