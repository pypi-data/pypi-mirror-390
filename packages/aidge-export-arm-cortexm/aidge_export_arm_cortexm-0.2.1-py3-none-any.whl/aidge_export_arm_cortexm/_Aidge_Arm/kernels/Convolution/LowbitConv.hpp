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

#ifndef __N2D2_EXPORT_ARM_CONV_CUSTOM_HPP__
#define __N2D2_EXPORT_ARM_CONV_CUSTOM_HPP__

#include <cmath>

#include "kernels/typedefs.hpp"
#include "assert.h"
#include "utils.hpp"
#include "kernels/Macs.hpp"
#include "kernels/subkernels_functions.hpp"

namespace N2D2_Export {

template<int NB_CHANNELS, 
         int CHANNELS_HEIGHT, int CHANNELS_WIDTH,
         int NB_OUTPUTS, 
         int OUTPUTS_HEIGHT, int OUTPUTS_WIDTH,
         int PADDING_Y, int PADDING_X,
         int STRIDE_Y, int STRIDE_X,
         int KERNEL_HEIGHT, int KERNEL_WIDTH,
         ActivationFunction_T ACTIVATION,
        //  // Memory mapping: inputs
        //  int INPUT_MEM_CONT_OFFSET,
        //  int INPUT_MEM_CONT_SIZE,
        //  int INPUT_MEM_WRAP_OFFSET,
        //  int INPUT_MEM_WRAP_SIZE,
        //  int INPUT_MEM_STRIDE,
        //  // Memory mapping: outputs
        //  int OUTPUT_MEM_CONT_OFFSET,
        //  int OUTPUT_MEM_CONT_SIZE,
        //  int OUTPUT_MEM_WRAP_OFFSET,
        //  int OUTPUT_MEM_WRAP_SIZE,
        //  int OUTPUT_MEM_STRIDE,
         typename Sum_T, typename Input_T, typename Output_T, 
         typename Weight_T, typename Bias_T, typename Rescaling_T>
__attribute__((always_inline)) inline static
void lowbitconvcellPropagate(const Input_T* __restrict inputs,
                                      Output_T* __restrict outputs,
                                      const Bias_T* __restrict biasses,
                                      const Weight_T* __restrict weights,
                                      const Rescaling_T& __restrict rescaling) 
{
    PackSupport infoPack = {0, 0};

    constexpr int bits_norm_in = (std::numeric_limits<Input_T>::digits >= 8) 
                        ? 8/std::ceil(8/(float)std::numeric_limits<Input_T>::digits) 
                        : 8/std::floor(8/(float)std::numeric_limits<Input_T>::digits);

    constexpr int bits_norm_wt = (std::numeric_limits<Weight_T>::digits >= 8) 
                        ? 8/std::ceil(8/(float)std::numeric_limits<Weight_T>::digits) 
                        : 8/std::floor(8/(float)std::numeric_limits<Weight_T>::digits);

    constexpr int INPUTS_BYTE
        = std::ceil(((NB_CHANNELS * bits_norm_in)
          + (NB_CHANNELS * bits_norm_in) % 8) / (float)8);
    constexpr int WEIGHTS_BYTE 
        = std::ceil(((NB_CHANNELS * bits_norm_wt)
          + (NB_CHANNELS * bits_norm_wt) % 8) / (float)8);

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

            for (int och = 0; och < NB_OUTPUTS; ++och) {
                Sum_T weightedSum = biasses[och];

                for (int sy = 0; sy < KERNEL_HEIGHT; ++sy) {

                    if (PADDING_Y != 0 && (sy < syMin || sy >= syMax)) {
                        continue;
                    }
                    const int inputsOffset = (iy + sy - PADDING_Y) * CHANNELS_WIDTH * INPUTS_BYTE
                                             + (ix - PADDING_X) * INPUTS_BYTE;

                    const int weightsOffset = och * KERNEL_HEIGHT * KERNEL_WIDTH * WEIGHTS_BYTE
                                              + sy * KERNEL_WIDTH * WEIGHTS_BYTE;

                    // if (PADDING_X == 0
                    //     && (NB_CHANNELS * std::numeric_limits<Weight_T>::digits % 8 == 0)
                    //     && (NB_CHANNELS * std::numeric_limits<Input_T>::digits % 8 == 0)) {
                    if (PADDING_X == 0
                        && (NB_CHANNELS * bits_norm_wt % 8 == 0)
                        && (NB_CHANNELS * bits_norm_in % 8 == 0)) {

                        macsOnRange<KERNEL_WIDTH * NB_CHANNELS>(inputs + inputsOffset,
                                                                weights + weightsOffset,
                                                                weightedSum);
                    } 
                    else {
                        for (int sx = 0; sx < KERNEL_WIDTH; ++sx) {
                            if(sx < sxMin || sx >= sxMax) {
                                continue;
                            }
                            macsOnRange<NB_CHANNELS>(inputs + inputsOffset + sx * INPUTS_BYTE,
                                                     weights + weightsOffset + sx * WEIGHTS_BYTE,
                                                     weightedSum);
                        }
                    }
                }
                Output_T output = sat<Output_T>(weightedSum,och, ACTIVATION, rescaling);
                compact_data_during_loop(output, outputs, outputOffset, infoPack);
            }
            compact_data_end_loop(outputs, outputOffset, infoPack);

            ix += STRIDE_X;
        }
        iy += STRIDE_Y;
    }
}


}   // N2D2_Export

#endif  // __N2D2_EXPORT_ARM_CONV_CUSTOM_HPP__
