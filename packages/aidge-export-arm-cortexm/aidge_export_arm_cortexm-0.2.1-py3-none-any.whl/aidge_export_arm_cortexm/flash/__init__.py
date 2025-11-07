"""Aidge Export for ARM CortexM

Use this module to generate CPP exports for ARM CortexM boards.
This module has to be used with the Aidge suite
"""
"""
Module flash - contient les outils de flashage et capture UART pour les exports STM32.
"""
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
BOARD_CONFIG_PATH = ROOT / "board_config.json"
from .flash_export import ( load_config as load_flash_config,
                           flash_with_pyocd,
                           parsing_uart_output,
                           read_serial_output,
                           flash_and_capture)

