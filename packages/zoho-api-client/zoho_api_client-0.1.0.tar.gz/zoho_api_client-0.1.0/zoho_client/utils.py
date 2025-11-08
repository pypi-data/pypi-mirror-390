"""Utilidades para el cliente de Zoho."""

import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura un logger básico.

    Args:
        name: Nombre del logger
        level: Nivel de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger