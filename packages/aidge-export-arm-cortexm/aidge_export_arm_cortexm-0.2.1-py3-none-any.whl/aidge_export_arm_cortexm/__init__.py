"""Aidge Export for ARM CortexM

Use this module to generate CPP exports for ARM CortexM boards.
This module has to be used with the Aidge suite
"""
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

from .export import *
from .export_registry import ExportLibAidgeARM, ExportLibCMSISNN
from .operators import *
from .utils import show_version, get_project_version
from .benchmark import *
from .flash import *