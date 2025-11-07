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

#ifndef __N2D2_EXPORT_CPP_MACS_HPP__
#define __N2D2_EXPORT_CPP_MACS_HPP__

#include <cstdint>
#include <limits>
#include <type_traits>
#include <cmsis_compiler.h>

namespace N2D2_Export {


template<typename Input_T>
inline static
uint32_t XTB16(uint32_t val)
{
    return std::is_unsigned<Input_T>::value ? __UXTB16(val) : __SXTB16(val);
}

template<int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         typename Input_T,
         typename Weight_T,
         typename Sum_T>
inline static
Sum_T dualMac(const Input_T* __restrict inputs,
              const Weight_T* __restrict weights,
              Sum_T weightedSum)
{
    weightedSum += inputs[0] * weights[0]
        + inputs[INPUTS_INC] * weights[WEIGHTS_INC];

    return weightedSum;
}

template<int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         typename Input_T,
         typename Weight_T,
         typename Sum_T,
         typename std::enable_if<std::is_floating_point<Input_T>::value>::type* = nullptr>
inline static
Sum_T quadMac(const Input_T* __restrict inputs,
              const Weight_T* __restrict weights,
              Sum_T weightedSum)
{
    weightedSum += inputs[0*INPUTS_INC] * weights[0*WEIGHTS_INC]
        + inputs[1*INPUTS_INC] * weights[1*WEIGHTS_INC]
        + inputs[2*INPUTS_INC] * weights[2*WEIGHTS_INC]
        + inputs[3*INPUTS_INC] * weights[3*WEIGHTS_INC];

    return weightedSum;
}

template<int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         typename Input_T,
         typename Weight_T,
         typename Sum_T,
         typename std::enable_if<!std::is_floating_point<Input_T>::value>::type* = nullptr>
inline static
Sum_T quadMac(const Input_T* __restrict inputs,
              const Weight_T* __restrict weights,
              Sum_T weightedSum)
{
    if(INPUTS_INC != 1 || WEIGHTS_INC != 1) {
        weightedSum += inputs[0*INPUTS_INC] * weights[0*WEIGHTS_INC]
            + inputs[1*INPUTS_INC] * weights[1*WEIGHTS_INC]
            + inputs[2*INPUTS_INC] * weights[2*WEIGHTS_INC]
            + inputs[3*INPUTS_INC] * weights[3*WEIGHTS_INC];

        return weightedSum;
    }

    // Inputs loading & preparation
    uint32_t in;
    memcpy((void*) &in, inputs, sizeof(in));

    uint32_t in1 = XTB16<Input_T>(in);
    uint32_t in2 = XTB16<Input_T>(in >> 8);

    // Weights loading & preparation
    uint32_t wt;
    memcpy((void*) &wt, weights, sizeof(wt));

    uint32_t wt1 = XTB16<Weight_T>(wt);
    uint32_t wt2 = XTB16<Weight_T>(wt >> 8);

    // Computation
    if(std::is_same<Sum_T, int32_t>::value) {
        weightedSum = __SMLAD(in1, wt1, weightedSum);
        weightedSum = __SMLAD(in2, wt2, weightedSum);
    }
    else {
        weightedSum = __SMLALD(in1, wt1, weightedSum);
        weightedSum = __SMLALD(in2, wt2, weightedSum);

    }

    return weightedSum;
}



// **************************************************************************
// * Multiply-accumulate the values in inputs and weights for NB_ITERATIONS *
// **************************************************************************

template<int NB_ITERATIONS,
         int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         class Input_T,
         class Weight_T,
         class Sum_T,
         typename std::enable_if<(NB_ITERATIONS == 0)>::type* = nullptr>
inline static
void macsOnRange(const Input_T* __restrict /*inputs*/,
                 const Weight_T* __restrict /*weights*/,
                 Sum_T& __restrict /*weightedSum*/)
{
    // Nothing to do
}

template<int NB_ITERATIONS,
         int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         class Input_T,
         class Weight_T,
         class Sum_T,
         typename std::enable_if<(NB_ITERATIONS == 1)>::type* = nullptr>
inline static
void macsOnRange(const Input_T* __restrict inputs,
                 const Weight_T* __restrict weights,
                 Sum_T& __restrict weightedSum)
{
    weightedSum += (*weights) * (*inputs);
}

template<int NB_ITERATIONS,
         int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         class Input_T,
         class Weight_T,
         class Sum_T,
         typename std::enable_if<(NB_ITERATIONS >= 2 && NB_ITERATIONS < 4)>::type* = nullptr>
inline static
void macsOnRange(const Input_T* __restrict inputs,
                 const Weight_T* __restrict weights,
                 Sum_T& __restrict weightedSum)
{
    weightedSum = dualMac<INPUTS_INC, WEIGHTS_INC>(inputs, weights, weightedSum);
    macsOnRange<NB_ITERATIONS - 2, INPUTS_INC, WEIGHTS_INC>(inputs + 2*INPUTS_INC,
                                                            weights + 2*WEIGHTS_INC,
                                                            weightedSum);
}

/**
 * @brief   MACs Processing
 * @details Performs NB_ITERATIONS MACs operations, storing results into the
 *          weightedSum variable.
 *
 * @tparam  NB_ITERATIONS   Number of MACs to perform
 * @tparam  INPUTS_INC      Input Stride
 * @tparam  WEIGHTS_INC     Weights Stride
 * @tparam  Input_T         Input Type
 *
 * @param   inputs          Pointer to inputs vector
 * @param   weights         Pointer to weights vector
 * @param   weightedSum     Pointer to weightedSum
*/
template<int NB_ITERATIONS,
         int INPUTS_INC = 1,
         int WEIGHTS_INC = 1,
         class Input_T,
         class Weight_T,
         class Sum_T,
         typename std::enable_if<(NB_ITERATIONS >= 4)>::type* = nullptr>
inline static
void macsOnRange(const Input_T* __restrict inputs,
                 const Weight_T* __restrict weights,
                 Sum_T& __restrict weightedSum)
{
    weightedSum = quadMac<INPUTS_INC, WEIGHTS_INC>(inputs, weights, weightedSum);
    macsOnRange<NB_ITERATIONS - 4, INPUTS_INC, WEIGHTS_INC>(inputs + 4*INPUTS_INC,
                                                            weights + 4*WEIGHTS_INC,
                                                            weightedSum);
}


}   // N2D2_Export

#endif  // __N2D2_EXPORT_CPP_MACS_HPP__
