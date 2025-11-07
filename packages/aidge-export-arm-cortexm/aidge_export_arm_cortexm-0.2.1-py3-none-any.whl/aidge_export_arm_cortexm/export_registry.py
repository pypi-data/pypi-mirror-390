from aidge_core.export_utils import ExportLib
from aidge_export_arm_cortexm import ROOT

class ExportLibAidgeARM(ExportLib):
    _name="aidge_arm"
    mem_section = ".nn_buffer_d1"

class ExportLibCMSISNN(ExportLib):
    _name="export_cmsisnn"

