"""
First-run bootstrap helpers for pyRofex-to-Excel.

This module handles:
- Interactive prompting of required pyRofex configuration on first run.
- Persisting prompted values into project .env.
- Normalizing workbook extension to .xlsx when workbook is missing.
- Refreshing runtime module-level configuration constants.
"""

import os
import sys
from pathlib import Path
from typing import Dict

from dotenv import set_key

from ..utils.logging import get_logger
from . import excel_config, pyrofex_config

logger = get_logger(__name__)

_PLACEHOLDER_VALUES = {
    "REPLACE_WITH_YOUR_USERNAME",
    "REPLACE_WITH_YOUR_PASSWORD",
    "REPLACE_WITH_YOUR_ACCOUNT",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _env_file_path() -> Path:
    return _project_root() / ".env"


def _is_missing_required(value: str | None) -> bool:
    if value is None:
        return True
    stripped = str(value).strip()
    return not stripped or stripped in _PLACEHOLDER_VALUES


def _prompt_password_with_mask(prompt_text: str) -> str:
    if os.name != "nt":
        from getpass import getpass

        return getpass(prompt_text)

    import msvcrt

    sys.stdout.write(prompt_text)
    sys.stdout.flush()

    chars = []

    while True:
        char = msvcrt.getwch()

        if char in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(chars)

        if char == "\003":
            raise KeyboardInterrupt

        if char in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue

        if char == "\b":
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue

        chars.append(char)
        sys.stdout.write("*")
        sys.stdout.flush()


def _broker_from_url(url: str) -> str:
    """Extract broker name from URL like https://api.cocos.xoms.com.ar/"""
    try:
        host = url.split("//", 1)[1].split("/")[0]  # api.cocos.xoms.com.ar
        parts = host.split(".")
        if len(parts) >= 5 and parts[0] == "api" and parts[2] == "xoms":
            return parts[1]
    except Exception:
        pass
    return ""


def _urls_from_broker(broker: str) -> tuple:
    """Build API and WS URLs from broker name."""
    b = broker.strip().lower()
    return f"https://api.{b}.xoms.com.ar/", f"wss://api.{b}.xoms.com.ar/"


def _prompt_value(key: str, current: str, default: str = "", secret: bool = False, label: str = "") -> str:
    display = label or key
    suggested = current if current and current not in _PLACEHOLDER_VALUES else default

    while True:
        if secret:
            prompt_text = f"{display}{' (enter para mantener)' if current and current not in _PLACEHOLDER_VALUES else ''}: "
            entered = _prompt_password_with_mask(prompt_text)
        else:
            if suggested:
                entered = input(f"{display} [{suggested}]: ").strip()
            else:
                entered = input(f"{display}: ").strip()

        if entered:
            return entered

        if suggested:
            return suggested

        logger.warning(f"{key} es requerido y no puede estar vacío")


def _persist_env_values(values: Dict[str, str]) -> bool:
    try:
        env_path = _env_file_path()
        env_path.parent.mkdir(parents=True, exist_ok=True)
        if not env_path.exists():
            env_path.write_text("", encoding="utf-8")

        for key, value in values.items():
            set_key(str(env_path), key, value, quote_mode="auto")

        logger.info(f"Configuración persistida en {env_path.name}")
        return True
    except Exception as e:
        logger.error(f"No se pudo guardar configuración en .env: {e}")
        return False


def _update_env(values: Dict[str, str]):
    for key, value in values.items():
        os.environ[key] = value


def _collect_current_pyrofex_values() -> Dict[str, str]:
    return {
        "PYROFEX_ENVIRONMENT": os.getenv("PYROFEX_ENVIRONMENT", pyrofex_config.ENVIRONMENT),
        "PYROFEX_API_URL": os.getenv("PYROFEX_API_URL", pyrofex_config.API_URL),
        "PYROFEX_WS_URL": os.getenv("PYROFEX_WS_URL", pyrofex_config.WS_URL),
        "PYROFEX_USER": os.getenv("PYROFEX_USER", pyrofex_config.USER),
        "PYROFEX_PASSWORD": os.getenv("PYROFEX_PASSWORD", pyrofex_config.PASSWORD),
        "PYROFEX_ACCOUNT": os.getenv("PYROFEX_ACCOUNT", pyrofex_config.ACCOUNT),
    }


def _prompt_required_pyrofex_values(current_values: Dict[str, str]) -> Dict[str, str]:
    logger.info("Primera ejecución detectada: completá los datos requeridos de pyRofex")

    values = dict(current_values)

    values["PYROFEX_USER"] = _prompt_value(
        "PYROFEX_USER",
        current=current_values["PYROFEX_USER"],
        label="Usuario (Matriz)",
    )
    values["PYROFEX_PASSWORD"] = _prompt_value(
        "PYROFEX_PASSWORD",
        current=current_values["PYROFEX_PASSWORD"],
        secret=True,
        label="Contraseña (Matriz)",
    )
    values["PYROFEX_ACCOUNT"] = _prompt_value(
        "PYROFEX_ACCOUNT",
        current=current_values["PYROFEX_ACCOUNT"],
        label="Nº Cuenta (Matriz)",
    )

    # PYROFEX_ENVIRONMENT is always LIVE — no prompt needed
    values["PYROFEX_ENVIRONMENT"] = "LIVE"

    default_broker = _broker_from_url(current_values.get("PYROFEX_API_URL", "")) or "cocos"
    broker = _prompt_value(
        "BROKER",
        current="",
        default=default_broker,
        label='Broker (ejemplo: ingresá "cocos" si usás api.cocos.xoms.com.ar)',
    )
    values["PYROFEX_API_URL"], values["PYROFEX_WS_URL"] = _urls_from_broker(broker)

    return values


def _prompt_excel_filename() -> Dict[str, str]:
    """Ask the user for the Excel workbook name and normalize to .xlsx."""
    current_file = os.getenv("EXCEL_FILE", excel_config.EXCEL_FILE)
    default_stem = Path(current_file).stem  # strip any extension

    raw = _prompt_value(
        "EXCEL_FILE",
        current="",
        default=default_stem,
        label="Nombre del archivo Excel (sin extensión)",
    )
    stem = Path(raw).stem  # strip extension if user typed one
    xlsx_name = f"{stem}.xlsx"
    return {"EXCEL_FILE": xlsx_name}


def _ensure_xlsx_when_workbook_missing() -> Dict[str, str]:
    updates: Dict[str, str] = {}

    excel_file = os.getenv("EXCEL_FILE", excel_config.EXCEL_FILE)
    excel_path = os.getenv("EXCEL_PATH", excel_config.EXCEL_PATH)

    workbook_path = Path(excel_path) / excel_file
    if workbook_path.exists():
        return updates

    suffix = Path(excel_file).suffix.lower()
    if suffix != ".xlsx":
        xlsx_name = f"{Path(excel_file).stem}.xlsx"
        updates["EXCEL_FILE"] = xlsx_name
        logger.info(
            f"No existe workbook configurado ({excel_file}). Se usará {xlsx_name} para bootstrap automático."
        )

    return updates


def refresh_runtime_config_modules():
    """Refresh module-level config constants from current environment values."""
    excel_config.EXCEL_FILE = os.getenv("EXCEL_FILE", excel_config.EXCEL_FILE)
    excel_config.EXCEL_PATH = os.getenv("EXCEL_PATH", excel_config.EXCEL_PATH)
    excel_config.EXCEL_SHEET_PRICES = os.getenv("EXCEL_SHEET_PRICES", excel_config.EXCEL_SHEET_PRICES)
    excel_config.EXCEL_SHEET_TICKERS = os.getenv("EXCEL_SHEET_TICKERS", excel_config.EXCEL_SHEET_TICKERS)
    excel_config.EXCEL_SHEET_TRADES = os.getenv("EXCEL_SHEET_TRADES", excel_config.EXCEL_SHEET_TRADES)
    excel_config.EXCEL_UPDATE_INTERVAL = float(os.getenv("EXCEL_UPDATE_INTERVAL", str(excel_config.EXCEL_UPDATE_INTERVAL)))
    excel_config.TRADES_SYNC_ENABLED = os.getenv("TRADES_SYNC_ENABLED", str(excel_config.TRADES_SYNC_ENABLED)).lower() == "true"
    excel_config.TRADES_REALTIME_ENABLED = os.getenv("TRADES_REALTIME_ENABLED", str(excel_config.TRADES_REALTIME_ENABLED)).lower() == "true"
    excel_config.TRADES_SYNC_INTERVAL_SECONDS = int(
        os.getenv("TRADES_SYNC_INTERVAL_SECONDS", str(excel_config.TRADES_SYNC_INTERVAL_SECONDS))
    )

    pyrofex_config.ENVIRONMENT = os.getenv("PYROFEX_ENVIRONMENT", pyrofex_config.ENVIRONMENT)
    pyrofex_config.API_URL = os.getenv("PYROFEX_API_URL", pyrofex_config.API_URL)
    pyrofex_config.WS_URL = os.getenv("PYROFEX_WS_URL", pyrofex_config.WS_URL)
    pyrofex_config.USER = os.getenv("PYROFEX_USER", pyrofex_config.USER)
    pyrofex_config.PASSWORD = os.getenv("PYROFEX_PASSWORD", pyrofex_config.PASSWORD)
    pyrofex_config.ACCOUNT = os.getenv("PYROFEX_ACCOUNT", pyrofex_config.ACCOUNT)
    pyrofex_config.CONNECTION_TIMEOUT_SECONDS = float(
        os.getenv("PYROFEX_CONNECTION_TIMEOUT_SECONDS", str(pyrofex_config.CONNECTION_TIMEOUT_SECONDS))
    )

    try:
        from ..market_data import api_client as api_client_module

        api_client_module.ENVIRONMENT = pyrofex_config.ENVIRONMENT
        api_client_module.API_URL = pyrofex_config.API_URL
        api_client_module.WS_URL = pyrofex_config.WS_URL
        api_client_module.USER = pyrofex_config.USER
        api_client_module.PASSWORD = pyrofex_config.PASSWORD
        api_client_module.ACCOUNT = pyrofex_config.ACCOUNT
        api_client_module.CONNECTION_TIMEOUT_SECONDS = pyrofex_config.CONNECTION_TIMEOUT_SECONDS
    except Exception as e:
        logger.debug(f"No se pudo refrescar constantes de api_client: {e}")


def run_first_time_bootstrap(force_reconfigure: bool = False) -> bool:
    """
    Run first-time bootstrap flow.

    Returns:
        bool: True if bootstrap completed successfully, False if bootstrap is required but cannot run.
    """
    current = _collect_current_pyrofex_values()
    required_missing = any(
        _is_missing_required(current[key])
        for key in ("PYROFEX_USER", "PYROFEX_PASSWORD", "PYROFEX_ACCOUNT")
    )

    accumulated_updates: Dict[str, str] = {}

    if force_reconfigure or required_missing:
        if not sys.stdin or not sys.stdin.isatty():
            if force_reconfigure:
                logger.error("Se solicitó reconfiguración, pero el entorno no es interactivo")
            else:
                logger.error("Faltan credenciales requeridas y el entorno no es interactivo para solicitarlas")
            logger.error("Configurá PYROFEX_USER, PYROFEX_PASSWORD y PYROFEX_ACCOUNT en .env")
            return False

        if force_reconfigure:
            logger.info("Reconfiguración solicitada: completá nuevamente los datos de pyRofex")

        prompted_values = _prompt_required_pyrofex_values(current)
        accumulated_updates.update(prompted_values)

        excel_name_updates = _prompt_excel_filename()
        accumulated_updates.update(excel_name_updates)

    if "EXCEL_FILE" not in accumulated_updates:
        excel_updates = _ensure_xlsx_when_workbook_missing()
        accumulated_updates.update(excel_updates)

    if accumulated_updates:
        _update_env(accumulated_updates)
        if not _persist_env_values(accumulated_updates):
            return False

    refresh_runtime_config_modules()
    return True
