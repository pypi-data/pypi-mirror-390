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

#ifndef __N2D2_EXPORT_CPP_CUSTOMFC_HPP__
#define __N2D2_EXPORT_CPP_CUSTOMFC_HPP__

#include <cmath>

#include "kernels/typedefs.hpp"
#include "assert.h"
#include "utils.hpp"
#include "kernels/Macs.hpp"
#include "kernels/subkernels_functions.hpp"

namespace N2D2_Export {

template<int NB_CHANNELS, int CHANNELS_HEIGHT, int CHANNELS_WIDTH,
         int NB_OUTPUTS, int OUTPUTS_HEIGHT, int OUTPUTS_WIDTH,
         ActivationFunction_T ACTIVATION,
         typename Sum_T, typename Input_T, typename Output_T, 
         typename Weight_T, typename Bias_T, typename Rescaling_T>
__attribute__((always_inline)) inline static
void lowbitfccellPropagate(const Input_T* __restrict inputs,
                                    Output_T* __restrict outputs,
                                    const Bias_T* __restrict biasses,
                                    const Weight_T* __restrict weights,
                                    const Rescaling_T& __restrict rescaling)
{
    static_assert(OUTPUTS_HEIGHT == 1, "Outputs height should be 1");
    static_assert(OUTPUTS_WIDTH == 1, "Outputs width should be 1");

    PackSupport infoPack = {0, 0};

    constexpr int INPUTS_BYTE
        = std::ceil(((NB_CHANNELS * std::numeric_limits<Input_T>::digits)
          + (NB_CHANNELS * std::numeric_limits<Input_T>::digits) % 8) / (float)8);
    constexpr int WEIGHTS_BYTE 
        = std::ceil(((NB_CHANNELS * std::numeric_limits<Weight_T>::digits)
          + (NB_CHANNELS * std::numeric_limits<Weight_T>::digits) % 8) / (float)8);

    int outputOffset = 0;
    for (int och = 0; och < NB_OUTPUTS; ++och) {
        Sum_T weightedSum = biasses[och];

        for (int iy = 0; iy < CHANNELS_HEIGHT; ++iy) {

            for (int ix = 0; ix < CHANNELS_WIDTH; ++ix) {

                const int weightsOffset = CHANNELS_HEIGHT * CHANNELS_WIDTH * WEIGHTS_BYTE * och 
                                            + (CHANNELS_WIDTH * iy + ix) * WEIGHTS_BYTE;
                const int inputsOffset = (CHANNELS_WIDTH * iy + ix) * INPUTS_BYTE;

                macsOnRange<NB_CHANNELS>(inputs + inputsOffset,
                                         weights + weightsOffset, 
                                         weightedSum);
            }
        }
        Output_T output = sat<Output_T>(weightedSum,och, ACTIVATION, rescaling);
        compact_data_during_loop(output, outputs, outputOffset, infoPack);
    }
    compact_data_end_loop(outputs, outputOffset, infoPack);
}

}   // N2D2_Export

#endif  // __N2D2_EXPORT_CPP_FC_HPP__
