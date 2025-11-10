"""
TentyPy Builder - Logger
Author: Keniding
Description: Sistema de logging
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str, level: int = logging.INFO, format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configurar logger

    Args:
        name: Nombre del logger
        level: Nivel de logging
        format_string: Formato personalizado

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        if format_string is None:
            format_string = "[%(levelname)s] %(message)s"

        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
