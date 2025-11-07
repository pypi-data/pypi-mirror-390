import aidge_core

from typing import Dict

datatype_converter_aidge2arm: Dict[aidge_core.dtype, str]  = {
    aidge_core.dtype.float64    : "double",
    aidge_core.dtype.float32    : "float",

    aidge_core.dtype.int32      : "data<32>",
    aidge_core.dtype.int16      : "data<16>",
    aidge_core.dtype.int8       : "data<8>",
    aidge_core.dtype.uint32     : "udata<32>",
    aidge_core.dtype.uint16     : "udata<16>",
    aidge_core.dtype.uint8      : "udata<8>",
    
    # Integer type without weightinterleaving
    # aidge_core.dtype.int7       : "data<8>",
    # aidge_core.dtype.int6       : "data<8>",
    # aidge_core.dtype.int5       : "data<8>",
    aidge_core.dtype.int4       : "data<8>",
    aidge_core.dtype.int3       : "data<8>",
    aidge_core.dtype.int2       : "data<8>",
    aidge_core.dtype.binary     : "data<8>",
        
    # aidge_core.dtype.uint7      : "udata<8>",
    # aidge_core.dtype.uint6      : "udata<8>",
    # aidge_core.dtype.uint5      : "udata<8>",
    aidge_core.dtype.uint4      : "udata<8>", 
    aidge_core.dtype.uint3      : "udata<8>",
    aidge_core.dtype.uint2      : "udata<8>", 
    
    # Integer type with weightinterleaving
    aidge_core.dtype.dual_int4       : "data<4>",
    aidge_core.dtype.dual_int3       : "data<3>",
    aidge_core.dtype.quad_int2       : "data<2>",
    aidge_core.dtype.octo_binary     : "data<1>",

    aidge_core.dtype.dual_uint4       : "udata<4>",
    aidge_core.dtype.dual_uint3       : "udata<3>",
    aidge_core.dtype.quad_uint2       : "udata<2>",
}

