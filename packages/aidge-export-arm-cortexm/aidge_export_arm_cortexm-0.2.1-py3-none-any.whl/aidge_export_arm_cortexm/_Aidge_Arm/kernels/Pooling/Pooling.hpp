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

#ifndef __N2D2_EXPORT_CPP_POOLING_HPP__
#define __N2D2_EXPORT_CPP_POOLING_HPP__

#include <cassert>
#include <cstdio>
#include "kernels/typedefs.hpp"
#include "kernels/utils.hpp"

namespace N2D2_Export {


template<int NB_CHANNELS,
        int CHANNELS_HEIGHT, int CHANNELS_WIDTH,
        int NB_OUTPUTS,
        int OUTPUTS_HEIGHT, int OUTPUTS_WIDTH,
        int PADDING_Y, int PADDING_X,
        int STRIDE_Y, int STRIDE_X,
        int POOL_HEIGHT, int POOL_WIDTH,
        Pooling_T POOLING_TYPE,
        ActivationFunction_T ACTIVATION,
        // Memory mapping: inputs
        int INPUT_MEM_CONT_OFFSET,
        int INPUT_MEM_CONT_SIZE,
        int INPUT_MEM_WRAP_OFFSET,
        int INPUT_MEM_WRAP_SIZE,
        int INPUT_MEM_STRIDE,
        // Memory mapping: outputs
        int OUTPUT_MEM_CONT_OFFSET,
        int OUTPUT_MEM_CONT_SIZE,
        int OUTPUT_MEM_WRAP_OFFSET,
        int OUTPUT_MEM_WRAP_SIZE,
        int OUTPUT_MEM_STRIDE,
        typename Input_T, typename Output_T>
__attribute__((always_inline)) inline static
void poolcellPropagate(const Input_T* __restrict inputs,
                       Output_T* __restrict outputs)
{
    static_assert(std::is_same<Input_T, Output_T>::value,
        "Input_T and Output_T must be the same.");
    static_assert(NB_CHANNELS == NB_OUTPUTS,
        "NB_CHANNELS should be equal to NB_OUTPUTS.");
    static_assert(POOLING_TYPE == Max || POOLING_TYPE == Average,
        "The export only supports Max and Average pooling.");
    static_assert(ACTIVATION == Linear,
        "The export only supports a Linear activation.");

    constexpr int OUTPUTS_HEIGHT_NOPAD
        = (CHANNELS_HEIGHT - POOL_HEIGHT + STRIDE_Y) / STRIDE_Y;
    constexpr int OUTPUTS_WIDTH_NOPAD
        = (CHANNELS_WIDTH - POOL_WIDTH + STRIDE_X) / STRIDE_X;

    for (int oy = 0; oy < OUTPUTS_HEIGHT; ++oy) {
        const int syMin = (PADDING_Y == 0) ? 0
            : max(PADDING_Y - (oy * STRIDE_Y), 0);
        const int syMax = (PADDING_Y == 0
                && OUTPUTS_HEIGHT == OUTPUTS_HEIGHT_NOPAD) ? POOL_HEIGHT
            : clamp(CHANNELS_HEIGHT + PADDING_Y - (oy * STRIDE_Y),
                    0, POOL_HEIGHT);
        const int iy = (oy * STRIDE_Y) - PADDING_Y;

        for (int ox = 0; ox < OUTPUTS_WIDTH; ++ox) {
            for (int output = 0; output < NB_OUTPUTS; ++output) {
                // moved to inner loop for collapsing -->
                const int sxMin = (PADDING_X == 0) ? 0
                    : max(PADDING_X - (ox * STRIDE_X), 0);
                const int sxMax = (PADDING_X == 0
                        && OUTPUTS_WIDTH == OUTPUTS_WIDTH_NOPAD)
                            ? POOL_WIDTH
                    : clamp(CHANNELS_WIDTH + PADDING_X - (ox * STRIDE_X),
                            0, POOL_WIDTH);
                const int ix = (ox * STRIDE_X) - PADDING_X;

                const int oPos = (ox + OUTPUTS_WIDTH * oy);
                int oOffset = OUTPUT_MEM_STRIDE * oPos;

                if (OUTPUT_MEM_WRAP_SIZE > 0 && oOffset >= OUTPUT_MEM_CONT_SIZE) {
                    oOffset += OUTPUT_MEM_WRAP_OFFSET - OUTPUT_MEM_CONT_OFFSET
                                - OUTPUT_MEM_CONT_SIZE;
                }
                // <--

                if (POOLING_TYPE == Max) {
                    Input_T maxVal = std::numeric_limits<Input_T>::lowest();

                    for (int sy = 0; sy < POOL_HEIGHT; ++sy) {
                        if ((PADDING_Y != 0
                                || OUTPUTS_HEIGHT != OUTPUTS_HEIGHT_NOPAD)
                            && sy >= syMax - syMin)
                        {
                            break;
                        }

                        const int iPos = ((sxMin + ix)
                                            + CHANNELS_WIDTH * (iy + syMin + sy));
                        int iOffset = INPUT_MEM_STRIDE * iPos;

                        // Wrapping cannot occur in the middle of a line, except if
                        // there is only one line (1D)!
                        bool wrapInRange = false;

                        if (INPUT_MEM_WRAP_SIZE > 0
                            && iOffset >= INPUT_MEM_CONT_SIZE)
                        {
                            iOffset += INPUT_MEM_WRAP_OFFSET - INPUT_MEM_CONT_OFFSET
                                        - INPUT_MEM_CONT_SIZE;
                        }
                        else if (INPUT_MEM_WRAP_SIZE > 0 && POOL_WIDTH > 1
                            && CHANNELS_HEIGHT == 1 // single line (1D)!
                            && iOffset + POOL_WIDTH * INPUT_MEM_STRIDE
                                > INPUT_MEM_CONT_SIZE)
                        {
                            wrapInRange = true;
                        }

                        for (int sx = 0; sx < POOL_WIDTH; ++sx) {
                            if ((PADDING_X != 0
                                    || OUTPUTS_WIDTH != OUTPUTS_WIDTH_NOPAD)
                                && sx >= sxMax - sxMin)
                            {
                                break;
                            }

                            int iOffsetInRange = iOffset + output
                                + sx * INPUT_MEM_STRIDE;

                            if (wrapInRange &&
                                iOffsetInRange >= INPUT_MEM_CONT_SIZE)
                            {
                                iOffsetInRange += INPUT_MEM_WRAP_OFFSET
                                            - INPUT_MEM_CONT_OFFSET
                                            - INPUT_MEM_CONT_SIZE;
                            }

                            if (inputs[iOffsetInRange] > maxVal)
                                maxVal = inputs[iOffsetInRange];
                        }
                    }

                    outputs[oOffset + output] = maxVal;
                }
                else if (POOLING_TYPE == Average) {
                    using Sum_T = typename std::conditional<std::is_floating_point<Input_T>::value, float, int32_t>::type;
                    Sum_T sum = 0;

                    for (int sy = 0; sy < POOL_HEIGHT; ++sy) {
                        if ((PADDING_Y != 0
                                || OUTPUTS_HEIGHT != OUTPUTS_HEIGHT_NOPAD)
                            && sy >= syMax - syMin)
                        {
                            break;
                        }

                        const int iPos = ((sxMin + ix)
                                            + CHANNELS_WIDTH * (iy + syMin + sy));
                        int iOffset = INPUT_MEM_STRIDE * iPos;

                        // Wrapping cannot occur in the middle of a line, except if
                        // there is only one line (1D)!
                        bool wrapInRange = false;

                        if (INPUT_MEM_WRAP_SIZE > 0
                            && iOffset >= INPUT_MEM_CONT_SIZE)
                        {
                            iOffset += INPUT_MEM_WRAP_OFFSET - INPUT_MEM_CONT_OFFSET
                                        - INPUT_MEM_CONT_SIZE;
                        }
                        else if (INPUT_MEM_WRAP_SIZE > 0 && POOL_WIDTH > 1
                            && CHANNELS_HEIGHT == 1 // single line (1D)!
                            && iOffset + POOL_WIDTH * INPUT_MEM_STRIDE
                                > INPUT_MEM_CONT_SIZE)
                        {
                            wrapInRange = true;
                        }

                        for (int sx = 0; sx < POOL_WIDTH; ++sx) {
                            if ((PADDING_X != 0
                                    || OUTPUTS_WIDTH != OUTPUTS_WIDTH_NOPAD)
                                && sx >= sxMax - sxMin)
                            {
                                break;
                            }

                            int iOffsetInRange = iOffset + output
                                + sx * INPUT_MEM_STRIDE;

                            if (wrapInRange &&
                                iOffsetInRange >= INPUT_MEM_CONT_SIZE)
                            {
                                iOffsetInRange += INPUT_MEM_WRAP_OFFSET
                                            - INPUT_MEM_CONT_OFFSET
                                            - INPUT_MEM_CONT_SIZE;
                            }

                            sum += inputs[iOffsetInRange];
                        }
                    }

                    outputs[oOffset + output] = (Output_T) (sum
                        / (POOL_HEIGHT * POOL_WIDTH));
                }
                else {
                    printf("The export only supports Max and Average pooling.");
                }
            }
        }
    }
}


}   // N2D2_Export

#endif  // __N2D2_EXPORT_CPP_POOLING_HPP__
