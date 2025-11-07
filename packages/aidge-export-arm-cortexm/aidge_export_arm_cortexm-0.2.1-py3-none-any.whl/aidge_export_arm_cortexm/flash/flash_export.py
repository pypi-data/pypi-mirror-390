"""
flash_export.py
-------------------
Script to flash a firmware ELF to a target microcontroller using pyOCD
and to capture its UART output based on a configurable JSON file.

Configuration is read from a JSON file (default: board_config.json).
The JSON configuration file should contain entries similar to the following example:
{
    "serial_port": "/dev/ttyACM0",
    "baudrate": 115200,
    "uart_timeout": 0.1,
    "uart_log_file": "uart_output.txt",
    "elf_path": "../bord_folder/bin/aidge_stm32.elf",
    "uart_capture_duration": 5
}

Usage:
    python3 flash_export.py [board_config.json]
"""

import json
import os
import sys
import time
import threading
import serial
import argparse
import numpy as np
import re
import aidge_core as ai
from pathlib import Path
from aidge_export_arm_cortexm.flash import BOARD_CONFIG_PATH
from pyocd.core.helpers import ConnectHelper
from pyocd.flash.file_programmer import FileProgrammer


def load_config(board_config:str)-> dict:
    """
    Load configuration parameters from a JSON file (e.g. ``board_config.json``).

    The file must exist and contain a valid JSON structure with parameters such as
    serial port, baudrate, timeout, log file path, and ELF path.

    :param board_config: Path to the configuration file (must be a JSON file).
    :type board_config: str

    :raises SystemExit: If the configuration file is missing or cannot be parsed.

    :return: Dictionary containing all configuration parameters loaded from the JSON file.
    :rtype: dict
    """
    config_path = Path(board_config)
    
    if not config_path.is_file():
        ai.Log.error(f"Configuration file {config_path} not found.")
        raise SystemExit(1)

    try:
        with config_path.open("r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        ai.Log.error(f"Error loading configuration file: {e}")
        raise SystemExit(1)


def read_serial_output(port: str, baudrate: int, timeout: float, log_file: str, stop_event: threading.Event,end_keyword: str,uart_capture_duration:float ) -> None:
    """
    Read UART output from a serial port and log it to a file.

    This function listens on the specified UART port and logs all incoming lines
    to a text file.
    The function stops when either the stop_event is set, the end_keyword is
    detected in the output, or the total capture time exceeds uart_capture_duration.

    :param port: Serial port name (e.g. ``/dev/ttyUSB0``, ``COM3``).
    :type port: str
    :param baudrate: Baudrate for UART communication.
    :type baudrate: int
    :param timeout: Read timeout in seconds.
    :type timeout: float
    :param log_file: Path to the file where UART logs will be written.
    :type log_file: str
    :param end_keyword: Keyword in UART output that triggers termination.
    :type end_keyword: str
    :param uart_capture_duration: Maximum total duration for UART capture in seconds.
    :type uart_capture_duration: float
    :param stop_event: Event object used to signal termination of UART capture.
    :type stop_event: threading.Event
    :raises serial.SerialException: If there is an error opening the serial port.
    """
    try:
        ai.Log.info(f"Connecting to serial port: {port} (baudrate={baudrate})")
        with serial.Serial(port, baudrate, timeout=timeout) as ser, open(log_file, "w") as logfile:
            ai.Log.info("Capturing UART output... \n")
            last_data_time = time.time()
            while not stop_event.is_set():
                if time.time() - last_data_time > uart_capture_duration:
                    ai.Log.info("UART capture duration exceeded. Stopping.")
                    stop_event.set()
                    break
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    ai.Log.info(f"[UART] {line}")
                    last_data_time = time.time()
                    logfile.write(line + "\n")
                    logfile.flush()
                    
                    if end_keyword in line:
                        ai.Log.info("End keyword detected in UART output. Stopping capture.")
                        stop_event.set()
                        break
    except serial.SerialException as e:
        ai.Log.error(f"Error connecting to serial port: {e}")
        return
        

def flash_with_pyocd(elf_path:str)-> None:
    """
    Connect to the target board using PyOCD and flash the provided ELF firmware file.

    This function uses PyOCD to connect to the target via a debug probe,
    flashes the specified ELF file, and resets the board to start execution.

    :param elf_path: Path to the compiled ELF file to flash onto the board.
    :type elf_path: str
    :raises SystemExit: If the ELF file is not found or if the connection to the target fails.
    """
    elf_path = Path(elf_path)
    
    if not elf_path.is_file():
        ai.Log.error(f"ELF file not found: {elf_path}")
        return

    ai.Log.info("Connecting to target device...")
    session = ConnectHelper.session_with_chosen_probe()
    if session is None:
        ai.Log.error("No target device detected.")
        return

    try:
        with session:
            target = session.target
            # Resume execution in case the MCU is halted.
            target.resume()
            ai.Log.info("Flashing the firmware ELF file...")
            programmer = FileProgrammer(session)
            programmer.program(str(elf_path),chip_erase=True)
            ai.Log.info("Firmware successfully flashed!")
            ai.Log.info("Resetting the target board...")
            target.reset_and_halt()
            ai.Log.info("Reset Firmware successfully.")
            #delay added to ensure the firmware starts correctly after flashing (for more stability)
            time.sleep(1)
            target.resume()
            ai.Log.info("Resume Firmware successfully.")
    except Exception as e:
        ai.Log.error(f"Failed to open UART port : {e}")
        raise SystemExit(1)     
            
def parsing_uart_output(filepath: str) -> dict:
    """
    Parse a UART log file and return either inference times or model output tensors.

    The function scans the file to detect either:
      - a line starting with ``inference_time``, in which case it returns a list of float values.
      - one of model outputs labeled with ``output_output_X:``, each followed by numerical values.

    :param filepath: Path to the UART log file to parse.
    :type filepath: str

    :return: A dictionary with two keys:
             - "timings": list of float values , otherwise None
             - "outputs": list of NumPy arrays , otherwise None     
    """
    outputs = []
    capturing = False
    current_values = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith("inference_time"):
                
                raw_data = line.split(":", 1)[1]
                timings = [float(v) for v in raw_data.strip().split() if v]
                return {"timings": timings,"outputs": None} 
            
            if line.startswith("output_output_"):
                capturing = True
                continue  # start capturing next lines

            if capturing:
                if any(n.isdigit() for n in line):
                    # Extract numerical values from the line
                    # and append them to the outputs.
                    values = [float(v) for v in line.strip().split() if v]
                    current_values.extend(values)
                    outputs.append(np.array(current_values))
                else:
                    # Stop capturing if a non-numeric line is encountered.
                    break

    return {"timings": None,"outputs": outputs}

def flash_and_capture(board_config: str,export_folder: str =None)-> None:
    """
    Perform firmware flashing and UART output capture based on a JSON configuration file.

    The configuration file (typically named ``board_config.json``) must be in JSON format
    and should contain all necessary parameters for flashing and serial communication. These parameters include:

    - ``serial_port`` (str): UART device to listen to (e.g. ``/dev/ttyACM0``, ``COM3``).
    - ``baudrate`` (int): UART communication speed.
    - ``uart_timeout`` (float): Timeout in seconds for UART reading.
    - ``uart_log_file`` (str): File where UART output will be saved.
    - ``elf_path`` (str): Path to the firmware ELF file to flash.
    - ``uart_capture_duration`` (float): Duration in seconds to capture UART output.

    If ``export_folder`` is provided, paths for ``elf_path`` and ``uart_log_file`` are resolved relative to it.

    A background thread is started to capture UART output while the firmware is being flashed using PyOCD.
    The UART capture stops after the specified duration.

    :param board_config: Path to the JSON configuration file (e.g. ``board_config.json``).
    :type board_config: str
    :param export_folder: Optional base folder containing ELF and UART output files.
    :type export_folder: str, optional
    :raises SystemExit: If UART initialization fails or flashing cannot be completed.
    """
    config = load_config(board_config)

    serial_port = config.get("serial_port")
    baudrate = config.get("baudrate")
    uart_timeout = config.get("uart_timeout")
    uart_log_file = config.get("uart_log_file")
    elf_path = config.get("elf_path")
    end_keyword = config.get("end_keyword")
    uart_capture_duration = config.get("uart_capture_duration")
    if export_folder:
        export_folder = Path(export_folder)
        elf_path = export_folder/elf_path
        uart_log_file =  export_folder/uart_log_file

    # Create an event to signal termination for the UART reading thread.
    stop_event = threading.Event()

    # Start the UART reading thread.
    serial_thread = threading.Thread(
        target=read_serial_output,
        args=(serial_port, baudrate, uart_timeout, uart_log_file, stop_event,end_keyword,uart_capture_duration),
    )
    serial_thread.start()

    # Short delay to ensure the serial port is ready.
    time.sleep(1)
    
    # Check if the thread has already terminated; this likely indicates an error.
    if not serial_thread.is_alive():
        sys.exit(1)
    
    # Flash the firmware and reset the target board.
    flash_with_pyocd(elf_path)

    serial_thread.join()
    ai.Log.info("UART capture terminated.")
    
def main():
    parser = argparse.ArgumentParser(description="Flash firmware and capture UART output.")
    parser.add_argument(
        "board_config",
        type=str,
        nargs="?",
        default=BOARD_CONFIG_PATH,
        help="Path to the board configuration JSON file (default: ./board_config.json).",
    )
    
    args = parser.parse_args()
    flash_and_capture(args.board_config)


if __name__ == "__main__":
    main()
