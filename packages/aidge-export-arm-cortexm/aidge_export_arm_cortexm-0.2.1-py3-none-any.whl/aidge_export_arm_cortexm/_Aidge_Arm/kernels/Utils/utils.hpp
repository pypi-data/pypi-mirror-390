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


#ifndef __N2D2_EXPORT_CPP_UTILS_HPP__
#define __N2D2_EXPORT_CPP_UTILS_HPP__

#include <stdio.h>
#include <stdint.h>
#include <type_traits>
#include <cstring>
#include <limits>

#include "kernels/typedefs.hpp"

namespace N2D2_Export {


template<typename T>
static T clamp(T v, T lo, T hi) 
{
    if(v < lo) {
        return lo;
    }
    else if(v > hi) {
        return hi;
    }
    else {
        return v;
    }
}

/**
 * @brief   Returns N/M rounded at the upper int
 *
 * @param[in]   N   First operand
 * @param[in]   M   Second operand
*/
template<typename T>
static T ceil(T N, T M) 
{
    if (N % M == 0) {
        return N / M;
    } else {
        return N / M + 1;
    }
}

template<typename Data_T,  
            typename std::enable_if<std::is_floating_point<Data_T>::value>::type* = nullptr>
static void fill_with_zero(Data_T* data, const unsigned int size) 
{
    // memset() doesn't work with floating-point numbers!
    for (unsigned int n = 0; n < size; ++n)
        data[n] = 0.0;
}

template<typename Data_T,  
            typename std::enable_if<!std::is_floating_point<Data_T>::value>::type* = nullptr>
static void fill_with_zero(Data_T* data, const unsigned int size) 
{
    std::memset(data, 0, size * sizeof(Data_T));
}
    
template<typename T>
static T max(T lhs, T rhs) 
{
    return (lhs >= rhs) ? lhs : rhs;
}

template<typename T>
static T min(T lhs, T rhs) 
{
    return (lhs < rhs) ? lhs : rhs;
}

template<typename Output_T, typename T,  
            typename std::enable_if<std::is_floating_point<T>::value>::type* = nullptr>
inline static Output_T saturate(T value, int32_t sat) 
{
    return value;
}

template<typename Output_T, typename T,  
            typename std::enable_if<!std::is_floating_point<T>::value>::type* = nullptr>
inline static Output_T saturate(T value, uint32_t sat) 
{
    return std::is_unsigned<Output_T>::value 
                    ? clamp((int)value, 0, (1 << sat) - 1)
                    : clamp((int)value, -(1 << (sat - 1)), (1 << (sat - 1)) - 1);
}

template<typename T,  
            typename std::enable_if<std::is_floating_point<T>::value>::type* = nullptr>
inline static T threshold() 
{
    return 0.0;
}

template<typename T,  
            typename std::enable_if<!std::is_floating_point<T>::value>::type* = nullptr>
inline static T threshold() 
{
    return (std::is_unsigned<T>::value)
        ? std::numeric_limits<T>::max() / 2 : 0;
}

template<typename Output_T, typename Rescaling_T, typename Sum_T>
inline static 
Output_T sat(Sum_T weightedSum, 
             int output, 
             ActivationFunction_T func, 
             const Rescaling_T& __restrict rescaling) 
{
    switch(func) {
        case Linear:
        case Saturation: {
            break;
        }
        case Rectifier: {
            if(weightedSum <= 0) weightedSum = 0;
            break;
        }
        default:
            printf("Unsupported activation function.");
    }

    // In N2D2 Export, saturate wants the number of bits to store the outputs
    // It was given as a global variable "NB_BITS"
    // Old code
    // return saturate<Output_T>(rescaling(weightedSum, output), NB_BITS);
    // For the current purposes, we adapt the nbbits depending the output datatype
    // Change it for future work in it is required
    return saturate<Output_T>(rescaling(weightedSum, output), 8*sizeof(Output_T));
}

template<typename Output_T>
inline static void saveOutputs(
    int NB_OUTPUTS,
    int OUTPUTS_HEIGHT, int OUTPUTS_WIDTH,
    int OUTPUT_MEM_CONT_OFFSET,
    int OUTPUT_MEM_CONT_SIZE,
    int OUTPUT_MEM_WRAP_OFFSET,
    int OUTPUT_MEM_WRAP_SIZE,
    int OUTPUT_MEM_STRIDE,
    const Output_T* __restrict outputs,
    FILE* pFile,
    Format_T format)
{
    if (format == Format_T::HWC) {
        fprintf(pFile, "(");
        for(int oy = 0; oy < OUTPUTS_HEIGHT; oy++) {
            fprintf(pFile, "(");

            for(int ox = 0; ox < OUTPUTS_WIDTH; ox++) {
                fprintf(pFile, "(");

                const int oPos = (ox + OUTPUTS_WIDTH * oy);
                int oOffset = OUTPUT_MEM_STRIDE * oPos;

                if (OUTPUT_MEM_WRAP_SIZE > 0
                    && oOffset >= OUTPUT_MEM_CONT_SIZE)
                {
                    oOffset += OUTPUT_MEM_WRAP_OFFSET - OUTPUT_MEM_CONT_OFFSET
                                - OUTPUT_MEM_CONT_SIZE;
                }

                for (int output = 0; output < NB_OUTPUTS; output++) {
                    if (std::is_floating_point<Output_T>::value)
                        fprintf(pFile, "%f", outputs[oOffset + output]);
                    else {
                        fprintf(pFile, "%d", outputs[oOffset + output]);
                    }
                    fprintf(pFile, ", ");
                }

                fprintf(pFile, "), \n");
            }

            fprintf(pFile, "), \n");
        }

        fprintf(pFile, ")\n");
    }
    else if (format == Format_T::CHW) {
        fprintf(pFile, "");
        for(int output = 0; output < NB_OUTPUTS; output++) {
            fprintf(pFile, "%d:\n", output);

            for(int oy = 0; oy < OUTPUTS_HEIGHT; oy++) {
                fprintf(pFile, "");

                for(int ox = 0; ox < OUTPUTS_WIDTH; ox++) {
                    const int oPos = (ox + OUTPUTS_WIDTH * oy);
                    int oOffset = OUTPUT_MEM_STRIDE * oPos;

                    if (OUTPUT_MEM_WRAP_SIZE > 0
                        && oOffset >= OUTPUT_MEM_CONT_SIZE)
                    {
                        oOffset += OUTPUT_MEM_WRAP_OFFSET
                            - OUTPUT_MEM_CONT_OFFSET - OUTPUT_MEM_CONT_SIZE;
                    }

                    if (std::is_floating_point<Output_T>::value)
                        fprintf(pFile, "%f", outputs[oOffset + output]);
                    else
                        fprintf(pFile, "%d", outputs[oOffset + output]);

                    fprintf(pFile, " ");
                }

                fprintf(pFile, "\n");
            }

            fprintf(pFile, "\n");
        }

        fprintf(pFile, "\n");
    }
    else {
        printf("Unknown format.");
    }
}

}   // N2D2_Export

#endif  // __N2D2_EXPORT_CPP_UTILS_HPP__
