import os
import math
import numpy as np
from pathlib import Path
from typing import Tuple, List

import aidge_core
import aidge_backend_cpu
from aidge_core.export_utils import ExportNode, ExportNodeCpp
from aidge_core.export_utils.code_generation import *
from aidge_export_arm_cortexm import ROOT
from aidge_export_arm_cortexm.export_registry import ExportLibAidgeARM
# from data_conversion import datatype_converter_aidge2arm
from aidge_export_arm_cortexm.data_conversion import datatype_converter_aidge2arm

##############################################
############## Export functions ##############
##############################################
# Note: to remove
def numpy_dtype2ctype(dtype):
    if dtype == np.int8:
        return "int8_t"
    elif dtype == np.int16:
        return "int16_t"
    elif dtype == np.int32:
        return "int32_t"
    elif dtype == np.int64:
        return "int64_t"
    elif dtype == np.float32:
        return "float"
    elif dtype == np.float64:
        return "double"
    # Add more dtype mappings as needed
    else:
        raise ValueError(f"Unsupported {dtype} dtype")


def export_params(name:str,
                  array: np.ndarray,
                  type_str: str,
                  filepath:str):

    # Get directory name of the file
    dirname = os.path.dirname(filepath)

    # If directory doesn't exist, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    generate_file(
        filepath,
        str(ROOT / "templates" / "data" / "parameters.jinja"),
        name = name,
        data_t = type_str,
        values = array.tolist(),
    )

def export_params_from_tensor(name:str,
                  tensor: aidge_core.Tensor,
                  type_str: str,
                  filepath:str):

    # Get directory name of the file
    dirname = os.path.dirname(filepath)

    # If directory doesn't exist, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    array = np.array(tensor).reshape(-1)

    generate_file(
        filepath,
        str(ROOT / "templates" / "data" / "parameters.jinja"),
        name = name,
        data_t = type_str,
        values = array.tolist(),
    )

##############################################
################### Actions ##################
##############################################

# @ExportLibAidgeARM.register("Producer", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.dual_int4)))
# class Producer_ARMCortexM(ExportNode):

#     def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
#         super().__init__(node, mem_info, conversion_map)

#         weights = self.operator.get_output(0)

#         self.values = np.array(weights).reshape(-1)


#     def export(self, export_folder: Path):
#         header_path = f"include/parameters/{self.attributes['name']}.hpp"
#         export_params(
#             name = self.attributes['out_name'][0],
#             array = self.values,
#             type_str = self.attributes["out_cdtype"][0],
#             filepath = str(export_folder / header_path))
#         return [header_path]

#     def forward(self):
#         # A Producer does nothing during forward
#         return []


# @ExportLibAidgeARM.register("Producer", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.any)))
# class Producer_ARMCortexM(ExportNode):

#     def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
#         super().__init__(node, mem_info, conversion_map)
#         self.values = np.array(self.operator.get_output(0))
#         if len(self.values.shape) == 4:  # Note: export in HWC
#             self.values = np.transpose(self.values, (0, 2, 3, 1))
#         # The following block of code is a dirty fix for FC
#         # The issue is that FC weight in Aidge are made for an CHW input
#         # Current export is made with HWC format
#         # So we need to reorder weights of the FC
#         # Note: it is not necessary if H and W != 1 (equivalent to in_dims length == 4)

#         if len(self.values.shape) == 2:
#             parents = node.get_children()
#             if len(parents) == 1 and list(parents)[0].type() == "FC":
#                 data_in = list(parents)[0].get_operator().get_input(0)
#                 if len(data_in.dims()) == 4:
#                     C = data_in.dims()[1]
#                     H = data_in.dims()[2]
#                     W = data_in.dims()[3]
#                     # Transpose weights to adapt the HWC
#                     self.values = self.values.reshape(-1, C, H, W).transpose(0, 2, 3, 1)

#     def export(self, export_folder: Path):
#         header_path = f"include/parameters/{self.attributes['name']}.hpp"
#         export_params(
#             name = self.attributes['out_name'][0],
#             array = self.values.reshape(-1),
#             type_str = self.attributes["out_cdtype"][0],
#             filepath = str(export_folder / header_path))
#         return [header_path]

#     def forward(self):
#         # A Producer does nothing during forward
#         return []

@ExportLibAidgeARM.register("Producer", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.any)))
class Producer_ARMCortexM(ExportNode):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.values = np.array(self.operator.get_output(0))
        self.ignore = node.attributes().has_attr("ignore")

    def export(self, export_folder: Path):
        if not self.ignore :
            header_path = f"include/parameters/{self.attributes['name']}.hpp"
            export_params(
                name = self.attributes['out_name'][0],
                array = self.values.reshape(-1),
                type_str = self.attributes["out_cdtype"][0],
                filepath = str(export_folder / header_path))
            return [header_path]
        return []

    def forward(self):
        # A Producer does nothing during forward
        return []


class Scaling():
    class ScalingMode:
        FLOAT_MULT32 = 0
        FIXED_MULT16 = 1
        FIXED_MULT32 = 2
        SINGLE_SHIFT = 3
        DOUBLE_SHIFT = 4

    def __init__(self, scaling_factor=0.0, nb_bits=8) -> None:
        self.scaling_factor = scaling_factor
        self.nb_bits = nb_bits

    def approximate_fixed_point_scaling(self, mode: int, scaling: float) -> Tuple[int, int]:
        """Calculate fixed point factor from floating point factor"""

        limit = (2**15 - 1) if mode == Scaling.ScalingMode.FIXED_MULT16 else (2**31 - 1)

        if scaling >= limit:
            if mode == Scaling.ScalingMode.FIXED_MULT16:
                print(f"Scaling ({scaling}) doesn't fit in FIXED_MULT16. Falling back to FIXED_MULT32.")
                mode = Scaling.ScalingMode.FIXED_MULT32
                return self.approximate_fixed_point_scaling(mode, scaling)
            else:
                raise RuntimeError(f"Scaling ({scaling}) doesn't fit in FIXED_MULT32.")

        max_nb_fractional_bits = 50
        nb_fractional_bits = min(math.floor(math.log(limit / scaling) / math.log(2.0)), max_nb_fractional_bits)

        scaling_fixed_point = round(scaling * (1 << nb_fractional_bits))
        return nb_fractional_bits, scaling_fixed_point

    def approximate_shift_scaling(self, scaling: float, nb_divisions: int) -> Tuple[List[int], float]:
        """Calculate single shift factor from floating point factor"""

        ROUNDING_THRESHOLD = 0.98

        assert nb_divisions > 0
        assert scaling <= 1.0

        precision = 0.0
        power_of_2_divs = [0] * nb_divisions

        for i_div in range(nb_divisions):
            if precision == 1.0:
                power_of_2_divs[i_div - 1] += 1
                power_of_2_divs[i_div] = power_of_2_divs[i_div - 1]
            else:
                exponent = math.ceil(math.log2(1.0 / (scaling * (1.0 - precision))))
                precision += 1.0 / (scaling * 2 ** exponent)
                power_of_2_divs[i_div] = exponent

        assert precision <= 1.0

        if precision >= ROUNDING_THRESHOLD:
            precision = 1.0
        elif precision < 1.0:
            precision += 1.0 / (scaling * 2 ** power_of_2_divs[-1])
            power_of_2_divs[-1] -= 1

        assert precision >= 1.0

        return power_of_2_divs, precision


    def __call__(self, mode:str) -> dict:
        """Get dictionnary of scale values in function of the mode
        Possible modes:
        - no_scaling
        - floating_point
        - fixed_point (16 or 32 bits)
        - single_shift
        - double_shift

        """

        if mode == "floating_point":
            self.scaling = {"scaling_type": "floating_point",
                            "scaling_value": self.scaling_factor}
        elif mode == "fixed_point":
            if self.nb_bits == 16:
                nb_fractional_bits, scaling_fixed_point = self.approximate_fixed_point_scaling(Scaling.ScalingMode.FIXED_MULT16, self.scaling_factor)
            else:
                nb_fractional_bits, scaling_fixed_point = self.approximate_fixed_point_scaling(Scaling.ScalingMode.FIXED_MULT32, self.scaling_factor)

            self.scaling = {"scaling_type": "fixed_point",
                            "scaling_value": scaling_fixed_point,
                            "fractional_bits": nb_fractional_bits}

        elif mode == "single_shift":
            shift_value, _ = self.approximate_shift_scaling(self.scaling_factor, 1)

            self.scaling = {"scaling_type": "single_shift",
                            "shift_value": shift_value[0]}

        elif mode == "double_shift":
            shift_value, _ = self.approximate_shift_scaling(self.scaling_factor, 2)

            self.scaling = {"scaling_type": "double_shift",
                            "shift_value_0": shift_value[0],
                            "shift_value_1": shift_value[1]}
        else:
            self.scaling = {"scaling_type": "no_scaling"}

        return self.scaling


# TODO : find a way to remove this dummy exportnode
@ExportLibAidgeARM.register("Pad", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.any)))
class Pad_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        raise NotImplementedError("Pad nodes is not implemented")




@ExportLibAidgeARM.register("ReLU", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class ReLU_ARMCortexM_float32(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "relu.jinja")

        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "relu.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Relu" / "aidge_relu_float32.h")

@ExportLibAidgeARM.register("Conv2D",
    aidge_core.ImplSpec(
        [ # Input specifications
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.nhwc),
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.nhwc),
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.any)
        ],
        [ # Output specifications
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.nhwc)
        ],
    ))
class Conv_ARMCortexM_float32(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        # No padding with Conv
        # Use PaddedConv to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "conv_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "Conv.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)

@ExportLibAidgeARM.register_generic("ArmPadConv2D", aidge_core.ImplSpec([
                                                                aidge_core.IOSpec(aidge_core.dtype.any),               # Input[0] : Input Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.dual_int4),      # Input[1] : Weight Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.int32)           # Input[2] : Bias Spec
                                                            ],
                                                            [
                                                                aidge_core.IOSpec(aidge_core.dtype.any)       # Output[0] : Output spec
                                                            ]))
class PadConvScaling_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
        super().__init__(node, mem_info, conversion_map)

        self.attributes["activation"] = "Linear"

        self.attributes["padding"] = [0, 0]
        if self.operator.attr.has_attr("Pad2D_0"):
            self.attributes["padding"] = self.operator.attr.get_attr("Pad2D_0").get_attr("begin_end_borders")

        self.attributes["kernel_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("kernel_dims")
        self.attributes["stride_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("stride_dims")
        self.attributes["dilation_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("dilation_dims")

        # Correct "in_chan" and "out_chan" that were taken from the compacted tensor
        self.attributes["in_chan"][0] = self.attributes["in_channels"]
        self.attributes["out_chan"][0] = self.attributes["out_channels"]

        if self.operator.attr.has_attr("ReLU_0"):
            self.attributes["activation"] = "Rectifier"

        # if self.operator.attr.has_attr("Scaling_0"):
        if self.operator.attr.has_attr("scaling_factor"):
            scaling_factor = self.operator.attr.scaling_factor
            self.attributes.update(Scaling(scaling_factor = scaling_factor)("floating_point"))

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "lowbit_conv_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "LowbitConv.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "subkernels_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)


@ExportLibAidgeARM.register_generic("ArmConv2D", aidge_core.ImplSpec([
                                                                aidge_core.IOSpec(aidge_core.dtype.any),               # Input[0] : Input Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.dual_int4),      # Input[1] : Weight Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.int32)           # Input[2] : Bias Spec
                                                            ],
                                                            [
                                                                aidge_core.IOSpec(aidge_core.dtype.any)       # Output[0] : Output spec
                                                            ]))
class ConvScaling_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
        super().__init__(node, mem_info, conversion_map)

        self.attributes["activation"] = "Linear"

        self.attributes["padding"] = [0, 0]
        if self.operator.attr.has_attr("Pad2D_0"):
            self.attributes["padding"] = self.operator.attr.get_attr("Pad2D_0").get_attr("begin_end_borders")

        self.attributes["kernel_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("kernel_dims")
        self.attributes["stride_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("stride_dims")
        self.attributes["dilation_dims"] = self.operator.attr.get_attr("Conv2D_0").get_attr("dilation_dims")

        # Correct "in_chan" and "out_chan" that were taken from the compacted tensor
        self.attributes["in_chan"][0] = self.attributes["in_channels"]
        self.attributes["out_chan"][0] = self.attributes["out_channels"]

        if self.operator.attr.has_attr("ReLU_0"):
            self.attributes["activation"] = "Rectifier"

        if self.operator.attr.has_attr("scaling_factor"):
            scaling_factor = self.operator.attr.scaling_factor
            self.attributes.update(Scaling(scaling_factor = scaling_factor)("floating_point"))


        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "lowbit_conv_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "LowbitConv.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "subkernels_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)


@ExportLibAidgeARM.register_generic("ArmFC", aidge_core.ImplSpec([
                                                                aidge_core.IOSpec(aidge_core.dtype.any),            # Input[0] : Input Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.dual_int4),      # Input[1] : Weight Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.int32)           # Input[2] : Bias Spec
                                                            ],
                                                            [
                                                                aidge_core.IOSpec(aidge_core.dtype.any)       # Output[0] : Output spec
                                                            ]))
class FCScaling_ARMCortexM_int4(ExportNodeCpp):
    def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
        super().__init__(node, mem_info, conversion_map)
        self.attributes["activation"] = "Linear"

        # # Correct "in_chan" and "out_chan" that were taken from the compacted tensor
        self.attributes["in_chan"][0] = self.attributes["in_channels"]
        self.attributes["out_chan"][0] = self.attributes["out_channels"]

        if self.operator.attr.has_attr("ReLU_0"):
            self.attributes["activation"] = "Rectifier"

        if self.operator.attr.has_attr("scaling_factor"):
            scaling_factor = self.operator.attr.scaling_factor
            self.attributes.update(Scaling(scaling_factor = scaling_factor)("floating_point"))

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "fc_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "lowbit_fc_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "FullyConnected" / "LowbitFc.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "subkernels_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)

# FIXME This take the precedence on float32 kernel due to poor management of IOSpec
# Need to update the IOSpec
# @ExportLibAidgeARM.register("MaxPooling2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.any)))
# class LowbitPooling_ARMCortexM(ExportNodeCpp):
#     def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
#         super().__init__(node, mem_info, conversion_map)

#         self.attributes["activation"] = "Linear"
#         self.attributes["pool_type"] = "Max"
#         # No padding with MaxPooling or AvgPooling
#         # Use PaddedMaxPooling/PaddedAvgPooling to add padding attribute
#         self.attributes["padding"] = [0, 0]

#         self.attributes["kernel_dims"] = node.get_operator().attr.kernel_dims
#         self.attributes["stride_dims"] = node.get_operator().attr.stride_dims

#         self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "pool_config.jinja")
#         self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "lowbit_pool_kernel.jinja")
#         self.include_list = []
#         self.kernels_to_copy = [
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Pooling" / "LowbitPooling.hpp")
#         ]

#         self.kernels_to_copy = [
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Pooling" / "LowbitPooling.hpp"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "subkernels_functions.hpp"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp"),
#             str(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp")
#         ]



# USING IMPLSPEC CONSTRUCTOR : INPUTS : const std::vector<ImplSpec::IOSpec>&, OUTPUTS : const std::vector<ImplSpec::IOSpec>&, ATTRIBUTES : const DynamicAttributes&>()
@ExportLibAidgeARM.register("Conv2D", aidge_core.ImplSpec(  [
                                                                aidge_core.IOSpec(aidge_core.dtype.any),    # Input[0] : Input Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.int4),   # Input[1] : Weight Spec
                                                                aidge_core.IOSpec(aidge_core.dtype.any)     # Input[2] : Bias Spec
                                                            ],
                                                            [
                                                                aidge_core.IOSpec(aidge_core.dtype.int4) # Output[0] : Output spec
                                                            ]))
class Conv_ARMCortexM_int4(ExportNodeCpp):
    def __init__(self, node, mem_info, conversion_map = datatype_converter_aidge2arm):
        super().__init__(node, mem_info, conversion_map)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        # No padding with Conv
        # Use PaddedConv to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "lowbit_conv_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "LowbitConv.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "subkernels_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)

@ExportLibAidgeARM.register("ConvDepthWise2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class ConvDW_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        # No padding with Conv
        # Use PaddedConv to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "conv_dw_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "ConvDW.hpp")

@ExportLibAidgeARM.register_metaop("PaddedConvDepthWise2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class PaddedConvDW_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        for n in self.operator.get_micro_graph().get_nodes():
            if n.type() == "Pad2D":
                self.attributes["padding"] = n.get_operator(
                ).attr.begin_end_borders
            if n.type() == "ConvDepthWise2D":
                self.attributes["kernel_dims"] = n.get_operator(
                ).attr.kernel_dims
                self.attributes["stride_dims"] = n.get_operator(
                ).attr.stride_dims
                self.attributes["dilation_dims"] = n.get_operator(
                ).attr.dilation_dims

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "conv_dw_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "ConvDW.hpp")



@ExportLibAidgeARM.register_metaop("PaddedConv2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class PaddedConv_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        for n in self.operator.get_micro_graph().get_nodes():
            if n.type() == "Pad2D":
                self.attributes["padding"] = n.get_operator(
                ).attr.begin_end_borders
            if n.type() == "Conv2D":
                self.attributes["kernel_dims"] = n.get_operator(
                ).attr.kernel_dims
                self.attributes["stride_dims"] = n.get_operator(
                ).attr.stride_dims
                self.attributes["dilation_dims"] = n.get_operator(
                ).attr.dilation_dims

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "conv_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "conv_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Convolution" / "Conv.hpp")

class Pooling_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes["pool_type"] = "None"
        # No padding with MaxPooling or AvgPooling
        # Use PaddedMaxPooling/PaddedAvgPooling to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "pool_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "pool_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Pooling" / "Pooling.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.kernel = node.get_operator().attr.kernel_dims
        self.stride = node.get_operator().attr.stride_dims


@ExportLibAidgeARM.register("FC",
    aidge_core.ImplSpec(
        [ # Input specifications
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.default),
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.any)
        ],
        [ # Output specifications
            aidge_core.IOSpec(aidge_core.dtype.any, aidge_core.dformat.any)
        ],
    ))
class FC_ARMCortexM_float32(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Linear"
        self.attributes.update(Scaling()("no_scaling"))
        # No padding with Conv
        # Use PaddedConv to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "fc_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "fc_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "FullyConnected" / "Fc.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        # self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)

@ExportLibAidgeARM.register("MaxPooling2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class MaxPooling_ARMCortexM(Pooling_ARMCortexM):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["pool_type"] = "Max"

@ExportLibAidgeARM.register("AvgPooling2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class AvgPooling_ARMCortexM(Pooling_ARMCortexM):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["pool_type"] = "Avg"

@ExportLibAidgeARM.register_metaop("FcReluScaling", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class FC_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation"] = "Rectifier"
        self.attributes.update(Scaling(self.operator.attr.scaling_factor,
                               self.operator.attr.quantized_nb_bits)("floating_point"))
        # No padding with Conv
        # Use PaddedConv to add padding attribute
        self.attributes["padding"] = [0, 0]

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "fc_config.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "fc_kernel.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "FullyConnected" / "Fc.hpp")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "Macs.hpp", fwd_include=False)
        # self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "swar_arm_acle.h", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "nn_scaling_functions.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "utils.hpp", fwd_include=False)
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "assert.h", fwd_include=False)

@ExportLibAidgeARM.register("Add", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Add_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "add.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "add.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Add" / "aidge_add_float32.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)

@ExportLibAidgeARM.register("BatchNorm2D", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class BatchNorm2D_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "batchnorm2d.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "batchnorm2d.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "BatchNorm" / "aidge_batchnorm2d_chw_float32.h")

@ExportLibAidgeARM.register("Sub", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Sub_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "sub.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "sub.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Sub" / "aidge_sub_float32.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)

@ExportLibAidgeARM.register("Mul", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Mul_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "mul.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "mul.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Mul" / "aidge_mul_float32.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "aidge_supportfunctions.h", fwd_include=False)

@ExportLibAidgeARM.register("Div", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Div_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "div.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "div.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Div" / "aidge_div.h")


@ExportLibAidgeARM.register("Softmax", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Softmax_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "softmax.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "softmax.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Softmax" / "aidge_softmax_chw_float32.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)

@ExportLibAidgeARM.register("Atan", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Atan_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "atan.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "atan.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Atan" / "aidge_atan.hpp")

@ExportLibAidgeARM.register("Reshape", aidge_core.ImplSpec([
                                                                aidge_core.IOSpec(aidge_core.dtype.any),
                                                                aidge_core.IOSpec(aidge_core.dtype.int64)
                                                           ],
                                                           [
                                                                aidge_core.IOSpec(aidge_core.dtype.any)
                                                           ]))
class Reshape_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "reshape.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "reshape.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Reshape" / "aidge_reshape.h")

@ExportLibAidgeARM.register("Slice", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Slice_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "slice.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "slice.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Slice" / "aidge_slice_float32.hpp")

@ExportLibAidgeARM.register("Concat", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Concat_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "concat.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "concat.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Concat" / "aidge_concat_float32.hpp")

@ExportLibAidgeARM.register("Sigmoid", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Sigmoid_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)
        self.attributes["activation_type"] = "\"SIGMOID\""

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "sigmoid.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "sigmoid.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Sigmoid" / "aidge_sigmoid.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)

@ExportLibAidgeARM.register("MatMul", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class MatMul_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "matmul.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "matmul.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "MatMul" / "aidge_matmul_chw_float32.h")
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Utils" / "typedefs.hpp", fwd_include=False)

@ExportLibAidgeARM.register("Transpose", aidge_core.ImplSpec(aidge_core.IOSpec(aidge_core.dtype.float32)))
class Transpose_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "transpose.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "transpose.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Transpose" / "aidge_transpose_chw_float32.h")

@ExportLibAidgeARM.register("Gather", aidge_core.ImplSpec([
                                                               aidge_core.IOSpec(aidge_core.dtype.float32),
                                                               aidge_core.IOSpec(aidge_core.dtype.int64)
                                                          ],
                                                          [
                                                               aidge_core.IOSpec(aidge_core.dtype.float32)
                                                          ]))
class Gather_ARMCortexM(ExportNodeCpp):
    def __init__(self, node, mem_info):
        super().__init__(node, mem_info)

        self.config_template = str(ROOT / "_Aidge_Arm" / "templates" / "configuration" / "gather.jinja")
        self.forward_template = str(ROOT / "_Aidge_Arm" / "templates" / "forward_call" / "gather.jinja")
        self.include_list = []
        self.add_kernel_to_copy(ROOT / "_Aidge_Arm" / "kernels" / "Gather" / "aidge_gather_chw_float32.h")
