/*
    (C) Copyright 2017 CEA LIST. All Rights Reserved.
    Contributor(s): N2D2 Team

    This software is governed by the CeCILL-C license under French law and
    abiding by the rules of distribution of free software.  You can  use,
    modify and/ or redistribute the software under the terms of the CeCILL-C
    license as circulated by CEA, CNRS and INRIA at the following URL
    "http://www.cecill.info".

    As a counterpart to the access to the source code and  rights to copy,
    modify and redistribute granted by the license, users are provided only
    with a limited warranty  and the software's author,  the holder of the
    economic rights,  and the successive licensors  have only  limited
    liability.

    The fact that you are presently reading this means that you have had
    knowledge of the CeCILL-C license and that you accept its terms.
*/

#ifndef __N2D2_EXPORT_CPP_CUSTOMPOOLING_HPP__
#define __N2D2_EXPORT_CPP_CUSTOMPOOLING_HPP__

#include <cmath>

#include "kernels/typedefs.hpp"
#include "assert.h"
#include "utils.hpp"
#include "kernels/Macs.hpp"
#include "kernels/subkernels_functions.hpp"


namespace N2D2_Export {

template<int NB_CHANNELS, int CHANNELS_HEIGHT, int CHANNELS_WIDTH,
        int NB_OUTPUTS, int OUTPUTS_HEIGHT, int OUTPUTS_WIDTH,
        int PADDING_Y, int PADDING_X,
        int STRIDE_Y, int STRIDE_X,
        int KERNEL_HEIGHT, int KERNEL_WIDTH,
        Pooling_T POOLING, ActivationFunction_T ACTIVATION,
        typename Input_T, typename Output_T>
__attribute__((always_inline)) inline static
void lowbitpoolcellPropagate(const Input_T* __restrict inputs,
                                    Output_T* __restrict outputs)
{
    static_assert(std::is_same<Input_T, Output_T>::value, "Input_T and Output_T must be the same.");
    static_assert(NB_CHANNELS == NB_OUTPUTS, "nb_channels should be equal to nb_outputs.");
    static_assert(POOLING == Max , "Only supports Max and Average pooling.");
    static_assert(ACTIVATION == Linear, "Only supports a Linear activation.");

    PackSupport infoPack = {0, 0};

    constexpr int INPUTS_BYTE
        = std::ceil(((NB_CHANNELS * std::numeric_limits<Input_T>::digits)
        + (NB_CHANNELS * std::numeric_limits<Input_T>::digits) % 8) / (float)8);
    constexpr int OUTPUTS_BYTE
        = std::ceil(((NB_OUTPUTS * std::numeric_limits<Output_T>::digits)
        + (NB_OUTPUTS * std::numeric_limits<Output_T>::digits) % 8) / (float)8);

    int outputOffset = 0;

    int iy = 0;
    for (int oy = 0; oy < OUTPUTS_HEIGHT; ++oy) {
        const int syMin = (PADDING_Y == 0) ? 0 : max(PADDING_Y - iy, 0);
        const int syMax = (PADDING_Y == 0) ? KERNEL_HEIGHT 
                                        : clamp(CHANNELS_HEIGHT + PADDING_Y - iy, 
                                                0, KERNEL_HEIGHT);

        int ix = 0;
        for (int ox = 0; ox < OUTPUTS_WIDTH; ++ox) {
            const int sxMin = (PADDING_X == 0) ? 0 : max(PADDING_X - ix, 0);
            const int sxMax = (PADDING_X == 0) ? KERNEL_WIDTH 
                                            : clamp(CHANNELS_WIDTH + PADDING_X - ix,  
                                                    0, KERNEL_WIDTH);

            int och_c = 0;
            while (och_c < OUTPUTS_BYTE) {

                // typename std::conditional<(!std::is_unsigned<Input_T>::value && 
                //         std::numeric_limits<Input_T>::digits == 32), data<32>, udata<32>>::type maxVal;
                // maxVal = decltype(maxVal)::lowest();
                typename std::conditional<(!std::is_unsigned<Input_T>::value && 
                        std::numeric_limits<Input_T>::digits == 32), int32_t, uint32_t>::type maxVal;
                maxVal = std::numeric_limits<decltype(maxVal)>::lowest();
                
                int nb_data = min(OUTPUTS_BYTE-och_c, get_pool_nbData(std::numeric_limits<Input_T>::digits));

                for (int sy = 0; sy < KERNEL_HEIGHT; ++sy) {

                    if (PADDING_Y != 0 && (sy < syMin || sy >= syMax)) {
                        continue;
                    }
                    const int inputsOffset = (iy + sy - PADDING_Y) * CHANNELS_WIDTH * INPUTS_BYTE
                                            + (ix - PADDING_X) * INPUTS_BYTE + och_c;

                    for (int sx = 0; sx < KERNEL_WIDTH; ++sx) {
                        if(sx < sxMin || sx >= sxMax) {
                            continue;
                        }
                        parallelMaxPooling(inputs + inputsOffset + sx*INPUTS_BYTE, maxVal, nb_data);
                    }
                }
                storeMaxPooling(outputs, outputOffset, maxVal, nb_data);
                och_c += nb_data;
            }

            ix += STRIDE_X;
        }
        iy += STRIDE_Y;
    }
}

}
#endif