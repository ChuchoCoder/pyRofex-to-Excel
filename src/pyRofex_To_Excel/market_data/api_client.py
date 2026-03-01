"""
Cliente API de pyRofex

Este módulo maneja la conexión y configuración de la API de pyRofex.
"""

import socket
import threading
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Any, Callable, Iterator, List, Set, Tuple

import pyRofex
import requests
from pyRofex.clients import rest_rfx as pyrofex_rest_rfx

from ..config.pyrofex_config import (ACCOUNT, API_URL,
                                     CONNECTION_TIMEOUT_SECONDS, ENVIRONMENT,
                                     PASSWORD, USER, WS_URL)
from ..utils.logging import get_logger
from .instrument_cache import InstrumentCache

logger = get_logger(__name__)


def _auth_url() -> str:
    return API_URL.rstrip("/") + "/auth/getToken"


def _request_auth_token(timeout_seconds: float) -> Tuple[bool, str, str]:
    """
    Pedir token de autenticación directamente a Matriz con timeout explícito.

    Returns:
        tuple[ok, token, reason]
    """
    user = USER.strip()
    password = PASSWORD.strip()

    headers = {
        "X-Username": user,
        "X-Password": password,
    }

    try:
        response = requests.post(
            _auth_url(),
            headers=headers,
            timeout=timeout_seconds,
        )
    except requests.exceptions.Timeout:
        return False, "", f"Timeout al autenticar contra Matriz tras {timeout_seconds:.1f}s"
    except requests.exceptions.ConnectionError as e:
        return False, "", f"Error de conexión al autenticar contra Matriz: {e}"
    except requests.exceptions.RequestException as e:
        return False, "", f"Error HTTP al autenticar contra Matriz: {e}"

    auth_token = response.headers.get("X-Auth-Token")

    if response.status_code in (401, 403):
        return False, "", "Credenciales rechazadas por Matriz (401/403)"

    if not response.ok:
        return (
            False,
            "",
            f"Matriz respondió {response.status_code} durante autenticación (no es error de credenciales)",
        )

    if not auth_token:
        return False, "", "Autenticación OK pero sin X-Auth-Token en la respuesta"

    return True, auth_token, ""


def _run_with_watchdog_timeout(
    callable_fn: Callable[[], Any], timeout_seconds: float
) -> Tuple[bool, Any, bool]:
    """
    Ejecutar una llamada potencialmente bloqueante con timeout duro.

    Nota: usa hilo daemon para evitar que un bloqueo interno de librería
    congele el flujo principal de la aplicación.

    Returns:
        Tuple[bool, object, bool]:
            - success
            - result u excepción
            - timed_out
    """
    result_queue: Queue[Tuple[bool, Any]] = Queue(maxsize=1)

    def _worker() -> None:
        try:
            result_queue.put((True, callable_fn()))
        except Exception as e:
            result_queue.put((False, e))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        return False, TimeoutError(f"Operación excedió timeout de {timeout_seconds:.1f}s"), True

    try:
        success, payload = result_queue.get_nowait()
        return success, payload, False
    except Empty:
        return False, RuntimeError("La operación finalizó sin resultado"), False


@contextmanager
def _temporary_pyrofex_rest_timeout(timeout_seconds: float) -> Iterator[None]:
    """
    Inyectar timeout por defecto en requests internos de pyRofex.

    pyRofex 0.5.0 no expone timeout configurable y usa requests.get/post
    sin parámetro timeout en RestClient, lo que puede bloquear por largos
    períodos según red/DNS/reintentos.
    """
    original_get = pyrofex_rest_rfx.requests.get
    original_post = pyrofex_rest_rfx.requests.post

    def _wrap_with_timeout(original_fn: Callable[..., Any]) -> Callable[..., Any]:
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("timeout", timeout_seconds)
            return original_fn(*args, **kwargs)

        return _wrapped

    pyrofex_rest_rfx.requests.get = _wrap_with_timeout(original_get)
    pyrofex_rest_rfx.requests.post = _wrap_with_timeout(original_post)
    try:
        yield
    finally:
        pyrofex_rest_rfx.requests.get = original_get
        pyrofex_rest_rfx.requests.post = original_post


class pyRofexClient:
    """Wrapper del cliente API de pyRofex."""
    
    def __init__(self):
        """Inicializar el cliente de pyRofex."""
        self.is_initialized = False
        self.is_authenticated = False
        self.instrument_cache = InstrumentCache(ttl_minutes=30)
        self._valid_instruments: Set[str] = set()
        
    def initialize(self):
        """Inicializar la conexión de pyRofex."""
        try:
            # Configurar parámetros de entorno
            pyRofex._set_environment_parameter('url', API_URL, getattr(pyRofex.Environment, ENVIRONMENT))
            pyRofex._set_environment_parameter('ws', WS_URL, getattr(pyRofex.Environment, ENVIRONMENT))
            
            # Inicializar
            logger.info(
                "Inicializando sesión pyRofex (timeout de conexión: %.1fs)",
                CONNECTION_TIMEOUT_SECONDS,
            )

            token_ok, auth_token, auth_reason = _request_auth_token(CONNECTION_TIMEOUT_SECONDS)
            if not token_ok:
                if "credenciales" in auth_reason.lower() or "401/403" in auth_reason:
                    print("\n" + "="*70)
                    print("\033[91m❌ FALLO DE AUTENTICACIÓN\033[0m")
                    print("="*70)
                    print("\033[91m🔐 PyRofex rechazó tus credenciales\033[0m")
                    print(f"\nDetalles del error: {auth_reason}")
                    print("\n📋 Qué pasó:")
                    print("   • La API rechazó usuario/contraseña")
                    print("   • Verificá que sean las credenciales de Matriz de tu ALyC")
                    print("="*70 + "\n")
                    logger.error("🔐 Fallo de autenticación: %s", auth_reason)
                else:
                    print("\n" + "="*70)
                    print("\033[91m⏱️ FALLO DE CONECTIVIDAD/AUTH\033[0m")
                    print("="*70)
                    print("\033[91mNo se pudo completar autenticación con Matriz\033[0m")
                    print(f"\nDetalles del error: {auth_reason}")
                    print("\n📋 Qué pasó:")
                    print("   • Este error NO indica necesariamente credenciales incorrectas")
                    print("   • Puede ser timeout/red o indisponibilidad temporal del backend")
                    print("="*70 + "\n")
                    logger.error("Fallo de conectividad/autenticación Matriz: %s", auth_reason)
                return False

            previous_socket_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(CONNECTION_TIMEOUT_SECONDS)
            try:
                with _temporary_pyrofex_rest_timeout(CONNECTION_TIMEOUT_SECONDS):
                    success, payload, timed_out = _run_with_watchdog_timeout(
                        lambda: pyRofex.initialize(
                            environment=getattr(pyRofex.Environment, ENVIRONMENT),
                            user=USER.strip(),
                            password=PASSWORD.strip(),
                            account=ACCOUNT.strip(),
                            active_token=auth_token,
                        ),
                        CONNECTION_TIMEOUT_SECONDS,
                    )
            finally:
                socket.setdefaulttimeout(previous_socket_timeout)

            if timed_out:
                print("\n" + "="*70)
                print("\033[91m⏱️ TIMEOUT DE CONEXIÓN\033[0m")
                print("="*70)
                print(
                    f"\033[91mNo se pudo completar la autenticación con Matriz en {CONNECTION_TIMEOUT_SECONDS:.1f}s\033[0m"
                )
                print("\n📋 Qué pasó:")
                print("   • La librería pyRofex quedó esperando respuesta de red/API")
                print("   • La app abortó la inicialización para evitar quedar clavada")
                print("\n🔧 Sugerencias:")
                print("   1. Verificá conectividad de red/VPN y estado de Matriz")
                print("   2. Probá aumentar PYROFEX_CONNECTION_TIMEOUT_SECONDS (ej: 30)")
                print("   3. Reintentá ejecutar la app")
                print("="*70 + "\n")
                logger.error(
                    "Timeout inicializando pyRofex tras %.1fs",
                    CONNECTION_TIMEOUT_SECONDS,
                )
                return False

            if not success:
                raise payload
            
            self.is_initialized = True
            self.is_authenticated = True
            logger.info(f"pyRofex inicializado con entorno: {ENVIRONMENT}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Verificar si es un error de autenticación
            if "Authentication fails" in error_msg or "Incorrect User or Password" in error_msg:
                print("\n" + "="*70)
                print("\033[91m❌ FALLO DE AUTENTICACIÓN\033[0m")
                print("="*70)
                print("\033[91m🔐 PyRofex rechazó tus credenciales\033[0m")
                print(f"\nDetalles del error: {error_msg}")
                print("\n📋 Qué pasó:")
                print("   • La API de PyRofex rechazó la combinación de usuario/contraseña")
                print("   • Las credenciales de tu cuenta son incorrectas o están vencidas")
                print("\n🔧 Cómo arreglarlo:")
                print("   1. Verificá tus credenciales en: https://www.cocos.xoms.com.ar/")
                print("   2. Actualizá tus credenciales en UNO de estos lugares:")
                print("      → Archivo .env (recomendado):")
                print("         PYROFEX_USER=tu_usuario")
                print("         PYROFEX_PASSWORD=tu_contraseña")
                print("         PYROFEX_ACCOUNT=tu_cuenta")
                print("      → O en src/pyRofex_To_Excel/config/pyrofex_config.py")
                print("\nConsejo de seguridad: ¡Nunca subas credenciales a git!")
                print("="*70 + "\n")
                
                logger.error(f"🔐 Fallo de autenticación: {error_msg}")
            else:
                logger.error(f"Fallo al inicializar pyRofex: {e}")
            
            return False

    def probe_matrix_connection(self) -> bool:
        """
        Verificar estado de autenticación con Matriz.

        Esta verificación NO realiza llamadas adicionales a endpoints REST.
        El criterio es que la autenticación (obtención de token) durante
        initialize() haya sido exitosa.

        Returns:
            bool: True si la autenticación está OK, False en caso contrario.
        """
        if not self.is_initialized or not self.is_authenticated:
            logger.error("No se pudo verificar autenticación con Matriz: sesión no autenticada")
            return False

        logger.info("Autenticación con Matriz verificada correctamente (sin probe REST adicional)")
        return True
    
    def fetch_available_instruments(self, force_refresh: bool = False) -> Set[str]:
        """
        Obtener instrumentos disponibles desde la API de pyRofex.
        Usa caché si está disponible y no expiró.
        
        Args:
            force_refresh: Forzar actualización desde API incluso si el caché es válido
            
        Returns:
            Set de símbolos de instrumentos válidos
        """
        try:
            # Intentar primero con caché a menos que se fuerce actualización
            if not force_refresh:
                cached_symbols = self.instrument_cache.get_instrument_symbols()
                if cached_symbols:
                    self._valid_instruments = cached_symbols
                    logger.info(f"Cargados {len(cached_symbols)} instrumentos desde caché")
                    return cached_symbols
            
            # Obtener desde API
            logger.info("Obteniendo instrumentos disponibles desde la API de pyRofex...")
            with _temporary_pyrofex_rest_timeout(CONNECTION_TIMEOUT_SECONDS):
                success, payload, timed_out = _run_with_watchdog_timeout(
                    pyRofex.get_detailed_instruments,
                    CONNECTION_TIMEOUT_SECONDS,
                )

            if timed_out:
                logger.error(
                    "Timeout obteniendo instrumentos tras %.1fs",
                    CONNECTION_TIMEOUT_SECONDS,
                )
                return set()

            if not success:
                raise payload

            instrumentsResponse = payload
            
            if not instrumentsResponse:
                logger.warning("No se devolvieron instrumentos desde la API")
                return set()
            
            instruments = instrumentsResponse['instruments']
            
            if not instruments:
                logger.warning("No se encontraron instrumentos en la respuesta de la API")
                return set()

            # Registrar estructura de respuesta para depuración
            logger.debug(f"La API devolvió {len(instruments)} instrumentos, tipo: {type(instruments)}")
            if instruments and len(instruments) > 0:
                logger.debug(f"Tipo del primer instrumento: {type(instruments[0])}, muestra: {instruments[0] if isinstance(instruments[0], str) else str(instruments[0])[:100]}")
            
            # Guardar en caché
            self.instrument_cache.save_instruments(
                instruments,
                metadata={
                    'environment': ENVIRONMENT,
                    'fetched_by': 'pyRofexClient'
                }
            )
            
            # Extraer símbolos - manejar tanto formatos dict como string
            symbols = set()
            for instrument in instruments:
                if isinstance(instrument, str):
                    # Ya es un string de símbolo
                    symbols.add(instrument)
                elif isinstance(instrument, dict):
                    # Extraer símbolo del dict
                    symbol = instrument.get('symbol') or instrument.get('instrumentId', {}).get('symbol')
                    if symbol:
                        symbols.add(symbol)
                else:
                    logger.warning(f"Tipo de instrumento inesperado: {type(instrument)}")
            
            self._valid_instruments = symbols
            logger.info(f"Obtenidos {len(symbols)} instrumentos desde la API")
            return symbols
            
        except Exception as e:
            logger.error(f"Error al obtener instrumentos: {e}")
            # Devolver símbolos en caché como fallback
            cached_symbols = self.instrument_cache.get_instrument_symbols()
            if cached_symbols:
                logger.warning(f"Usando instrumentos en caché como fallback ({len(cached_symbols)} símbolos)")
                self._valid_instruments = cached_symbols
                return cached_symbols
            return set()
    
    def validate_symbols(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validar símbolos contra instrumentos disponibles.
        
        Args:
            symbols: Lista de símbolos a validar
            
        Returns:
            Tupla de (símbolos_válidos, símbolos_inválidos)
        """
        if not self._valid_instruments:
            logger.warning("No hay instrumentos cargados, obteniendo ahora...")
            self.fetch_available_instruments()
        
        if not self._valid_instruments:
            logger.error("No se pueden validar símbolos - no hay instrumentos disponibles")
            return symbols, []  # Permitir todos los símbolos si no podemos validar
        
        valid = []
        invalid = []
        
        for symbol in symbols:
            if symbol in self._valid_instruments:
                valid.append(symbol)
            else:
                invalid.append(symbol)
        
        if invalid:
            logger.warning(f"Se encontraron {len(invalid)} símbolos inválidos: {invalid[:5]}{'...' if len(invalid) > 5 else ''}")
        
        logger.info(f"Validación de símbolos: {len(valid)} válidos, {len(invalid)} inválidos de {len(symbols)} totales")
        return valid, invalid
    
    def get_market_data(self, symbols, entries=None):
        """Obtener datos de mercado para símbolos."""
        if not self.is_initialized:
            raise RuntimeError("Cliente no inicializado. Llamá a initialize() primero.")
            
        if entries is None:
            # Solicitar todas las entradas de datos de mercado disponibles necesarias para las columnas de Excel
            entries = [
                pyRofex.MarketDataEntry.BIDS,               # Mejor compra (BI)
                pyRofex.MarketDataEntry.OFFERS,             # Mejor venta (OF)
                pyRofex.MarketDataEntry.LAST,               # Última operación (LA)
                pyRofex.MarketDataEntry.OPENING_PRICE,      # Precio de apertura (OP)
                pyRofex.MarketDataEntry.CLOSING_PRICE,      # Cierre anterior (CL)
                pyRofex.MarketDataEntry.HIGH_PRICE,         # Precio máximo (HI)
                pyRofex.MarketDataEntry.LOW_PRICE,          # Precio mínimo (LO)
                pyRofex.MarketDataEntry.TRADE_EFFECTIVE_VOLUME,  # Monto operado (EV)
                pyRofex.MarketDataEntry.NOMINAL_VOLUME,     # Volume (NV)
                pyRofex.MarketDataEntry.TRADE_COUNT,        # Operations/number of trades (TC)
            ]
            
        try:
            return pyRofex.get_market_data(symbols, entries)
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            raise
    
    def subscribe_market_data(self, symbols):
        """
        Suscribirse a datos de mercado en tiempo real.
        
        IMPORTANTE: Se espera que los símbolos ya hayan sido validados previamente
        en _validate_and_filter_symbols() para evitar validación redundante.
        
        Args:
            symbols: Lista de símbolos pre-validados a los que suscribirse
            
        Returns:
            bool: True si la suscripción fue exitosa, False en caso contrario
        """
        if not self.is_initialized:
            raise RuntimeError("Cliente no inicializado. Llamá a initialize() primero.")
        
        logger.debug(f"Suscribiendo a {len(symbols)} símbolos pre-validados")
        
        # Definir entradas de datos de mercado necesarias para las columnas de Excel
        entries = [
            pyRofex.MarketDataEntry.BIDS,               # Mejor compra (BI)
            pyRofex.MarketDataEntry.OFFERS,             # Mejor venta (OF)
            pyRofex.MarketDataEntry.LAST,               # Última operación (LA)
            pyRofex.MarketDataEntry.OPENING_PRICE,      # Precio de apertura (OP)
            pyRofex.MarketDataEntry.CLOSING_PRICE,      # Cierre anterior (CL)
            pyRofex.MarketDataEntry.HIGH_PRICE,         # Precio máximo (HI)
            pyRofex.MarketDataEntry.LOW_PRICE,          # Precio mínimo (LO)
            pyRofex.MarketDataEntry.TRADE_EFFECTIVE_VOLUME,  # Monto operado (EV)
            pyRofex.MarketDataEntry.NOMINAL_VOLUME,     # Volumen (NV)
            pyRofex.MarketDataEntry.TRADE_COUNT,        # Operaciones/cantidad de operaciones (TC)
        ]
            
        try:
            pyRofex.market_data_subscription(tickers=symbols, entries=entries)
            logger.info(f"Suscripto a datos de mercado para {len(symbols)} símbolos")
            return True
        except Exception as e:
            logger.error(f"Fallo al suscribirse a datos de mercado: {e}")
            return False
    
    def set_market_data_handler(self, handler):
        """Registrar (agregar) el manejador de mensajes de datos de mercado (API pyRofex 0.5.x)."""
        if not callable(handler):
            raise ValueError("El manejador debe ser invocable")
        # pyRofex 0.5.0 provee add_websocket_market_data_handler
        if hasattr(pyRofex, 'add_websocket_market_data_handler'):
            pyRofex.add_websocket_market_data_handler(handler)
            logger.info("Manejador de datos de mercado registrado")
        else:
            raise AttributeError("El módulo pyRofex no tiene add_websocket_market_data_handler")
    
    def set_error_handler(self, handler):
        """Registrar (agregar) el manejador de errores de websocket.""" 
        if not callable(handler):
            raise ValueError("El manejador debe ser invocable")
        if hasattr(pyRofex, 'add_websocket_error_handler'):
            pyRofex.add_websocket_error_handler(handler)
            logger.info("Manejador de errores registrado")
        else:
            logger.warning("pyRofex no tiene add_websocket_error_handler; manejador no configurado")
    
    def set_exception_handler(self, handler):
        """Configurar el manejador de excepciones de websocket (el nombre difiere en 0.5.x)."""
        if not callable(handler):
            raise ValueError("El manejador debe ser invocable")
        if hasattr(pyRofex, 'set_websocket_exception_handler'):
            pyRofex.set_websocket_exception_handler(handler)
            logger.info("Manejador de excepciones configurado")
        else:
            logger.warning("pyRofex no tiene set_websocket_exception_handler; manejador de excepciones no configurado")
    
    def subscribe_order_reports(self):
        """
        Subscribe to order reports via WebSocket.
        Provides real-time updates for order status changes and executions.
        """
        if not self.is_initialized:
            raise RuntimeError("Cliente no inicializado. Llamá a initialize() primero.")
        
        try:
            pyRofex.order_report_subscription()
            logger.info("Suscripto a reportes de órdenes")
            return True
        except Exception as e:
            logger.error(f"Fallo al suscribirse a reportes de órdenes: {e}")
            return False
    
    def set_order_report_handler(self, handler):
        """
        Register handler for order report messages.
        
        Args:
            handler: Callable that receives order report messages
        """
        if not callable(handler):
            raise ValueError("El manejador debe ser invocable")
        
        if hasattr(pyRofex, 'add_websocket_order_report_handler'):
            pyRofex.add_websocket_order_report_handler(handler)
            logger.info("Manejador de reportes de órdenes registrado")
        else:
            logger.warning("pyRofex no tiene add_websocket_order_report_handler; manejador no configurado")
    
    def get_filled_orders(self):
        """
        Fetch all filled/partially filled orders via REST API.
        
        Calls GET /rest/order/filleds endpoint.
        
        Returns:
            dict: Response containing filled orders, or None on error
                {
                    'status': 'OK',
                    'orders': [
                        {
                            'orderId': str,
                            'clOrdId': str,
                            'execId': str,
                            'accountId': {'id': str},
                            'instrumentId': {'marketId': str, 'symbol': str},
                            'price': float,
                            'orderQty': int,
                            'ordType': str,
                            'side': str,
                            'timeInForce': str,
                            'transactTime': str,
                            'avgPx': float,
                            'lastPx': float,
                            'lastQty': int,
                            'cumQty': int,
                            'leavesQty': int,
                            'status': str,
                            'text': str
                        },
                        ...
                    ]
                }
        """
        if not self.is_initialized:
            raise RuntimeError("Cliente no inicializado. Llamá a initialize() primero.")
        
        try:
            # pyRofex provides get_order_status for individual orders
            # For filled orders, we need to use the REST endpoint directly
            # The pyRofex library doesn't have a direct method for /rest/order/filleds
            # So we'll use get_all_orders which should return all orders
            
            logger.debug(f"Fetching filled orders for account {ACCOUNT}...")
            
            # Try using pyRofex's get_all_orders if available
            if hasattr(pyRofex, 'get_all_orders'):
                response = pyRofex.get_all_orders(account_id=ACCOUNT)
            else:
                # pyRofex doesn't have get_all_orders, use custom HTTP request
                logger.debug("Using custom HTTP request for filled orders endpoint")

                # Access the auth token from pyRofex's environment config
                try:
                    from pyRofex.components.enums import Environment
                    from pyRofex.components.globals import environment_config
                    
                    env = getattr(Environment, ENVIRONMENT)
                    auth_token = environment_config.get(env, {}).get('token')
                    
                    if not auth_token:
                        logger.error("Cannot fetch filled orders: No auth token in pyRofex environment config")
                        return None
                    
                    # Build request
                    headers = {
                        'X-Auth-Token': auth_token
                    }
                    url = f"{API_URL}rest/order/filleds"
                    params = {'accountId': ACCOUNT}
                    
                    logger.debug(f"Calling {url} with accountId={ACCOUNT}")
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    response.raise_for_status()
                    response = response.json()
                    
                except ImportError as ie:
                    logger.error(f"Cannot import pyRofex internals: {ie}")
                    return None
                except requests.exceptions.RequestException as re:
                    logger.error(f"HTTP request failed: {re}")
                    return None
            
            # Validate response
            if not response or response.get('status') != 'OK':
                logger.debug(f"Filled orders request failed or returned non-OK status: {response}")
                return None
            
            orders = response.get('orders', [])
            logger.debug(f"Fetched {len(orders)} filled orders from API")
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching filled orders: {e}", exc_info=True)
            return None
    
    def close_connection(self):
        """Cerrar la conexión de pyRofex."""
        if self.is_initialized:
            try:
                pyRofex.close_websocket_connection()
                logger.info("Conexión de pyRofex cerrada")
            except Exception as e:
                logger.warning(f"Error al cerrar conexión: {e}")
        
        self.is_initialized = False
        self.is_authenticated = False