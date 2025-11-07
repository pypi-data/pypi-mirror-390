from importlib.metadata import version

def show_version():
    version_aidge_export_arm_cortexm = version("aidge_export_arm_cortexm")
    print(f"Aidge Export Arm Cortexm: {version_aidge_export_arm_cortexm}")

def get_project_version()->str:
    return version("aidge_export_arm_cortexm")

