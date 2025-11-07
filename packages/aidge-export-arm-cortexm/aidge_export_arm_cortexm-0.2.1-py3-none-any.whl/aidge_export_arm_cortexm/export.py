import os
import shutil
from pathlib import Path
from aidge_export_arm_cortexm import ROOT
from aidge_export_arm_cortexm.export_registry import ExportLibAidgeARM
# from aidge_export_arm_cortexm.utils.converter import numpy_dtype2ctype

from aidge_core.mem_info import compute_default_mem_info, generate_optimized_memory_info
from aidge_core.export_utils import scheduler_export


BOARD_PATH : str = ROOT / "boards"

BOARDS_MAP: dict[str, Path] = {
    "stm32h7" : BOARD_PATH / "stm32" / "H7",
    "stm32f7" : BOARD_PATH / "stm32" / "F7",
}

def export(export_folder_name,
           graphview,
           scheduler = None,
           board:str ="stm32h7",
           mem_wrapping = False):

    scheduler_export(
        scheduler,
        export_folder_name,
        ExportLibAidgeARM,
        memory_manager=generate_optimized_memory_info,
        memory_manager_args={"stats_folder": f"{export_folder_name}/stats", "wrapping": mem_wrapping }
    )

    gen_board_files(export_folder_name, board)


def supported_boards() -> list[str]:
    return BOARDS_MAP.keys()

def gen_board_files(path:str, board:str)->None:
    if board not in supported_boards():
        joint_board_str = "\n\t-".join(supported_boards())
        raise ValueError(f"Board {board} is not supported, supported board are:\n\t-{joint_board_str}")

    if isinstance(path, str): path = Path(path)
    # Create dnn directory if not exist
    dnn_folder = path / "dnn"
    os.makedirs(str(dnn_folder), exist_ok=True)

    # Determine which board the user wants
    # to select correct config
    # Copy all static files in the export
    shutil.copytree(BOARDS_MAP[board], str(path), dirs_exist_ok=True)
