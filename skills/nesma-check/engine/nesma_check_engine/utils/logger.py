"""统一日志配置。格式: [{level}] [{module}:{func}:{line}] {message}"""
import logging
import sys

_CONFIGURED = False

def configure_logging(quiet: bool = False, debug: bool = False) -> logging.Logger:
    global _CONFIGURED
    if _CONFIGURED:
        return logging.getLogger("nesma_check_engine")
    _CONFIGURED = True
    logger = logging.getLogger("nesma_check_engine")
    level = logging.DEBUG if debug else (logging.WARNING if quiet else logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(
        "[{levelname}] [{module}:{funcName}:{line}] {message}", style="{"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def get_logger(name: str | None = None) -> logging.Logger:
    base = "nesma_check_engine"
    return logging.getLogger(f"{base}.{name}" if name else base)
