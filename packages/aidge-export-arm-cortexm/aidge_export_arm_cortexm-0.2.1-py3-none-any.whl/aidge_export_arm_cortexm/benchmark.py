import os
from subprocess import run, DEVNULL, CalledProcessError
import numpy as np
import aidge_core
import aidge_core.export_utils
import aidge_export_arm_cortexm
import aidge_backend_cpu
from pathlib import Path
from aidge_core.export_utils import generate_file, data_conversion
from aidge_export_arm_cortexm import ROOT
from aidge_export_arm_cortexm.export_registry import ExportLibAidgeARM, ExportLibCMSISNN
from aidge_export_arm_cortexm.operators import *
from aidge_export_arm_cortexm.flash import BOARD_CONFIG_PATH

# Default target board for export and benchmarking.
# Can be overridden externally before calling any function that uses it.
# Example: aidge_export_arm_cortexm.benchmark.board = "stm32f7"
BENCHMARK_BOARD = "stm32h7"
USE_DOCKER = True
# Number max of trial to catch the UART
MAX_RETRIES = 5

def _image_exists(image_name):
    """Helper function to check if a Docker image exist
    """
    result = run(
        ['docker', 'image', 'inspect', image_name],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return result.returncode == 0

def generate_call_function_arm_cortex_m(export_folder: str, call_function: str, board: str) -> None:
    generate_file(
        str(Path(export_folder) / "Src" / "main.c"),
        str(ROOT / "templates" / "main_call" / str("main_" + board + ".jinja")),
        call_function=call_function
    )

def measure_inference_time(model: aidge_core.GraphView, input_data: list[str, np.ndarray], nb_warmup: int = 10, nb_iterations: int = 10000) -> list[float]:
    # load and set up the model
    operator_type: str = model.get_ordered_outputs()[0][0].get_operator().type()
    export_folder :str = f"{operator_type.lower()}_export_arm_inference"
    board=BENCHMARK_BOARD
    model.set_backend("cpu")

    # create input Tensor list for the GraphView
    # === 1. Creation and injection of inputs ===

    ordered_inputs: list[aidge_core.Tensor] = []
    inputs_name: list[str] = []

    for i in input_data:
        nb_dims = len(i[1].shape)
        if nb_dims == 3:
            ordered_inputs.append(aidge_core.Tensor(i[1].transpose(0,2,1).reshape(i[1].shape).copy()))
        if nb_dims == 4:
            ordered_inputs.append(aidge_core.Tensor(np.transpose(i[1], axes=(0,2,3,1)).reshape(i[1].shape).copy()))
        else:
            ordered_inputs.append(aidge_core.Tensor(i[1]))

    for i, inp in enumerate(model.get_ordered_inputs()):
        op = inp[0].get_operator()
        op.set_input(i, ordered_inputs[i])

    # === 2. Propagation of dimensions ===
    model.forward_dims([t.dims() for t in ordered_inputs])

    # === 3. Scheduler generation ===
    scheduler = aidge_core.SequentialScheduler(model)
    scheduler.generate_scheduling()

    # === 4. Exporting code (DNN/, Makefile, Src/ etc) ===
    print("  ├─Exporting model ...")
    aidge_export_arm_cortexm.export(
        export_folder,
        graphview=model,
        scheduler=scheduler,
        board=board
    )

    # === 5. Generating input files ===
    print("  ├─Generating input .h files...")
    for i, (node, idx) in enumerate(model.get_ordered_inputs()):
        input_tensor = node.get_operator().get_input(idx)
        in_node_input, in_node_input_idx = node.input(idx)
        in_name = f"{node.name()}_input_{idx}" if in_node_input is None else f"{in_node_input.name()}_output_{in_node_input_idx}"
        inputs_name.append(in_name)
        aidge_core.export_utils.generate_input_file(export_folder=export_folder, array_name=in_name, tensor=input_tensor)

    # === 6. Generating main.c + print_output.hpp files ===
    print("  ├─Generating inference_time.hpp + main.c ...")
    outputs_name, outputs_dtype, outputs_size = [], [], []
    for node, idx in model.get_ordered_outputs():
        outputs_name.append(f"{node.name()}_output_{idx}")
        out_tensor = node.get_operator().get_output(idx)
        outputs_dtype.append(data_conversion.aidge2c(out_tensor.dtype()))
        outputs_size.append(out_tensor.size())

    generate_call_function_arm_cortex_m(Path(export_folder), "inference_time", board=board)
    generate_file(
        str(Path(export_folder)/"Src"/"inference_time.hpp"),
        str(ROOT / "templates" / "main_call" / "inference_time.jinja"),
        func_name="model_forward",
        board=board,
        inputs_name=inputs_name,
        nb_iterations=nb_iterations,
        nb_warmup=nb_warmup,
        outputs_name=outputs_name,
        outputs_dtype=outputs_dtype,
        outputs_size=outputs_size
    )


    # === 7. Compilation firmware ===
    print("  ├─Compiling firmware...")

    log_path = Path(export_folder)/"export_log.log"
    # Clean logs
    if log_path.exists():
        log_path.unlink()

    with log_path.open("a") as log_file:
        try:
            if USE_DOCKER:
                if not _image_exists("arm:arm-none-eabi_compiler"):
                    run(['make', 'build_image_docker'], cwd=export_folder, check=True, stdout=log_file, stderr=log_file)
                run(['make', 'build_export_docker'], cwd=export_folder, check=True, stdout=log_file, stderr=log_file)
            else:
                run(['make', 'build'], cwd=export_folder, check=True, stdout=log_file, stderr=log_file)
        except CalledProcessError as e:
            raise RuntimeError(f"Fail to build export {export_folder}.\nError log available at: {str(log_path)}.") from e

    # === 8. Flash STM32 + UART  and Reading outputs from UART ===

    # Attempt to flash and capture UART output multiple times to handle flashing instability.
    #
    # In some cases, the firmware may not start correctly due to an unreliable flashing process,
    # leading to no UART output or incomplete logs. This loop retries flashing and UART capture
    # up to MAX_RETRIES times.
    #
    # At each attempt:
    # 1. The firmware is flashed.
    # 2. UART output is captured and parsed.
    # 3. If the output file is missing or contains no valid outputs, another attempt is made.
    #
    # The loop exits early as soon as valid outputs are captured.

    timings = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  ├─Flashing and capturing attempt {attempt}/{MAX_RETRIES}")
        aidge_export_arm_cortexm.flash_and_capture(BOARD_CONFIG_PATH, export_folder=export_folder)
        # Check if the file uart_output exists
        uart_output_file = Path(export_folder) / "uart_output.txt"
        if not uart_output_file.is_file():
            aidge_core.Log.error(f"UART output file not found: {uart_output_file}")
            continue  # restart the loop

        # === 9. Reading outputs from UART ===
        parsed_uart = aidge_export_arm_cortexm.parsing_uart_output(uart_output_file)
        timings = parsed_uart["timings"]

        if timings:  # timings not empty
            break
        else :
            aidge_core.Log.error("No timings captured in uart_output.txt")
            continue

    print("  ├─Completed UART output capture.")

    if not timings:
        aidge_core.Log.fatal("No inference timings captured.No outputs captured. Check uart_ouput.txt and please restart the benchmark; the firmware might not have started properly on the board")
        raise SystemExit(1)

    print("  └─Inference time done.")

    return timings

def compute_output(model: aidge_core.GraphView, input_data: list[tuple[str, np.ndarray]]) -> list[np.ndarray]:

    operator_type: str = model.get_ordered_outputs()[0][0].get_operator().type()
    export_folder :str = f"{operator_type.lower()}_export_arm"
    board=BENCHMARK_BOARD

    model.set_backend("cpu")

    # === 1. Creation and injection of inputs ===
    ordered_inputs: list[aidge_core.Tensor] = []
    inputs_name: list[str] = []

    for name, array in input_data:
        nb_dims = len(array.shape)
        if nb_dims == 3:
            array = array.transpose(0,2,1).reshape(array.shape).copy()
        elif nb_dims == 4:
            array = np.transpose(array, axes=(0,2,3,1)).reshape(array.shape).copy()

        tensor = aidge_core.Tensor(array)
        tensor.set_backend("cpu")
        tensor.set_datatype(aidge_core.dtype.float32)
        ordered_inputs.append(tensor)


    for i, (node, idx) in enumerate(model.get_ordered_inputs()):
        node.get_operator().set_input(idx, ordered_inputs[i])

    # === 2. Propagation of dimensions ===
    model.forward_dims([t.dims() for t in ordered_inputs])

    # === 3. Scheduler generation ===
    scheduler = aidge_core.SequentialScheduler(model)
    scheduler.generate_scheduling()

    # === 4. Exporting code (DNN/, Makefile, Src/ etc) ===
    print("  ├─Exporting model ...")
    aidge_export_arm_cortexm.export(
        export_folder,
        graphview=model,
        scheduler=scheduler,
        board=board
    )

    # === 5. Generating input files ===
    print("  ├─Generating input .h files...")
    for i, (node, idx) in enumerate(model.get_ordered_inputs()):
        input_tensor = node.get_operator().get_input(idx)
        in_node_input, in_node_input_idx = node.input(idx)
        in_name = f"{node.name()}_input_{idx}" if in_node_input is None else f"{in_node_input.name()}_output_{in_node_input_idx}"
        inputs_name.append(in_name)
        aidge_core.export_utils.generate_input_file(export_folder=export_folder, array_name=in_name, tensor=input_tensor)

    # === 6. Generating main.c + print_output.hpp files ===
    print("  ├─Generating print_output.hpp + main.c ...")
    outputs_name, outputs_dtype, outputs_size = [], [], []
    for node, idx in model.get_ordered_outputs():
        outputs_name.append(f"{node.name()}_output_{idx}")
        out_tensor = node.get_operator().get_output(idx)
        outputs_dtype.append(data_conversion.aidge2c(out_tensor.dtype()))
        outputs_size.append(out_tensor.size())

    generate_call_function_arm_cortex_m(Path(export_folder), "print_output", board=board)
    generate_file(
        str(Path(export_folder)/"Src"/"print_output.hpp"),
        str(ROOT / "templates" / "main_call" / "print_output.jinja"),
        func_name="model_forward",
        inputs_name=inputs_name,
        outputs_name=outputs_name,
        outputs_dtype=outputs_dtype,
        outputs_size=outputs_size
    )

    # === 7. Compilation firmware ===
    print("  ├─Compiling firmware...")
    log_path = Path(export_folder)/"export_log.log"
    with log_path.open("a") as log_file:
        run(['make', 'build'], cwd=export_folder, check=True, stdout=log_file, stderr=log_file)

    # === 8. Flash STM32 + UART  and Reading outputs from UART ===

    # Attempt to flash and capture UART output multiple times to handle flashing instability.
    #
    # In some cases, the firmware may not start correctly due to an unreliable flashing process,
    # leading to no UART output or incomplete logs. This loop retries flashing and UART capture
    # up to MAX_RETRIES times.
    #
    # At each attempt:
    # 1. The firmware is flashed.
    # 2. UART output is captured and parsed.
    # 3. If the output file is missing or contains no valid outputs, another attempt is made.
    #
    # The loop exits early as soon as valid outputs are captured.

    outputs = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  ├─Flashing and capturing attempt {attempt}/{MAX_RETRIES}")
        aidge_export_arm_cortexm.flash_and_capture(BOARD_CONFIG_PATH, export_folder=export_folder)

    # Check if the file uart_output exists
        uart_output_file = Path(export_folder) / "uart_output.txt"
        if not uart_output_file.is_file():
            aidge_core.Log.error(f"UART output file not found: {uart_output_file}")
            continue  # Restart the loop

# === 9. Reading outputs from UART ===
        parsed_uart = aidge_export_arm_cortexm.parsing_uart_output(uart_output_file)
        outputs = parsed_uart["outputs"]

        if outputs:  # outputs not empty
            break
        else :
            aidge_core.Log.error("No outputs captured in uart_output.txt")
            continue

    print("  └─Completed UART output capture.")
    if not outputs:
        aidge_core.Log.error("No outputs captured. Check uart_ouput.txt and please restart the benchmark; the firmware might not have started properly on the board")
        raise SystemExit(1)

    # === 10. Reshape the outputs  ===

    for i, (node, idx) in enumerate(model.get_ordered_outputs()):
        dims = node.get_operator().get_output(idx).dims()
        nb_dims = len(dims)

        dims_permutted = dims
        if nb_dims == 3:
            dims_permutted = [dims[0], dims[2], dims[1]]
        elif nb_dims == 4:
            dims_permutted = [dims[0], dims[2], dims[3], dims[1]]

        if np.prod(dims) != outputs[i].size:
            aidge_core.Log.fatal("Incompatible export output size ({outputs[i].size}) with required shape {dims}", outputs[i].size, dims)
            raise SystemExit(1)

        outputs[i] = outputs[i].reshape(dims_permutted)

        if nb_dims == 3:
            outputs[i] = outputs[i].transpose(0, 2, 1)
        elif nb_dims == 4:
            outputs[i] = outputs[i].transpose(0, 3, 1, 2)

    print("  └─Compute output done.")

    return outputs