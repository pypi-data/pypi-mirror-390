/**
 ******************************************************************************
 * @file     subkernels_functions.hpp
 * @brief    Header file for the network subkernels
 * 
 ******************************************************************************
 * @attention
 * 
 * (C) Copyright 2021 CEA LIST. All Rights Reserved.
 *  Contributor(s): Vincent TEMPLIER (vincent.templier@cea.fr)
 * 
 * This file is not part of the open source version of N2D2 and is NOT under
 * the CeCILL-C license. This code is the property of the CEA. It can not be
 * copied or disseminated without its authorization.
 * 
 ******************************************************************************
 */

#ifndef __SUBKERNELS_FUNCTIONS_H__
#define __SUBKERNELS_FUNCTIONS_H__

#include <cstring>
#include <cmsis_compiler.h>
#include "typedefs.hpp"
#include "assert.h"


// ----------------------------------------------------------------------------
// -------------------------- Compression functions ---------------------------
// ----------------------------------------------------------------------------

/**
 * @brief   Compact data during a loop with an accumulator
 * @details This function is used in the network functions to compress 
 *          and store a value in the outputs vector. The function adds 
 *          the value to an accumulator. If the accumulator is full 
 *          (ie all the available slots are taken), then the accumulator
 *          is stored in the outputs. Otherwise, the accumulator temporaly
 *          keeps the previous values and it is shifted by 
 *          the number of bits required to store the quantized values.
 * 
 * @param[in]     value        Value to be stored in the accumulator
 * @param[in,out] outputs      Pointer to compressed output vector
 * @param[in,out] outputOffset Pointer to the current output index
 * @param[in,out] infoPack     Object containing the accumulator
 * @returns                    None
 * 
 */
template<typename Output_T, typename std::enable_if_t<std::numeric_limits<Output_T>::digits < 8, int> = 0>
__attribute__((always_inline)) static inline
void compact_data_during_loop (Output_T value,
                               Output_T* __restrict outputs,
                               int& outputOffset,
                               PackSupport& infoPack)
{
    if (std::numeric_limits<Output_T>::digits < 8) {
        constexpr uint8_t mask = (1U << std::numeric_limits<Output_T>::digits) - 1;
        constexpr uint8_t nbSlot = ceil((double)8/std::numeric_limits<Output_T>::digits);

        infoPack.accumulator |= value.value & mask;
        infoPack.cptAccumulator += 1;

        if (infoPack.cptAccumulator == nbSlot) {
            outputs[outputOffset] = (Output_T) infoPack.accumulator;
            ++outputOffset;
            infoPack.cptAccumulator = 0;
            infoPack.accumulator = 0;
        }
        else {
            infoPack.accumulator <<= std::numeric_limits<Output_T>::digits;
        }
    } else {
        outputs[outputOffset] = (Output_T) value;
        ++outputOffset;
    }
}

template<typename Output_T, typename std::enable_if_t<std::numeric_limits<Output_T>::digits >= 8, int> = 0>
__attribute__((always_inline)) static inline
void compact_data_during_loop (const Output_T value,
                               Output_T* __restrict outputs,
                               int& outputOffset,
                               PackSupport& infoPack)
{
    outputs[outputOffset] = value;
}

/**
 * @brief   Compact data after a loop with an accumulator
 * @details It may happen that the accumulator is not completely filled
 *          after calling "compact_data_during_loop" and the stored 
 *          quantized values in the accumulator have not been saved
 *          in the outputs. Thus, this function adds extra zeros to the
 *          accumulator until it is full. Then the accumulator is 
 *          stored in the outputs. 
 *          This function should always be called at the end of a loop
 *          where "compact_data_during_loop" is called
 * 
 * @param[in,out] outputs      Pointer to compressed output vector
 * @param[in,out] outputOffset Current output index
 * @param[in,out] infoPack     Object containing the accumulator
 * @returns                    None
 * 
 */
template<typename Output_T, typename std::enable_if_t<std::numeric_limits<Output_T>::digits < 8, int> = 0>
__attribute__((always_inline)) static inline
void compact_data_end_loop (Output_T* __restrict outputs,
                            int& outputOffset,
                            PackSupport& infoPack)
{
    if (std::numeric_limits<Output_T>::digits < 8) {
    
        // if data still accumulated but not stored
        if (infoPack.cptAccumulator != 0) {
            constexpr unsigned int nbSlot = ceil((double)8/std::numeric_limits<Output_T>::digits);

            // Add extra zero to shift data to the left
            infoPack.cptAccumulator += 1;
            while (infoPack.cptAccumulator < nbSlot) {
                infoPack.accumulator <<= std::numeric_limits<Output_T>::digits;
                infoPack.cptAccumulator += 1;
            }
            outputs[outputOffset] = infoPack.accumulator;
            ++outputOffset;
            infoPack.cptAccumulator = 0;
            infoPack.accumulator = 0;
        }
    }
}

template<typename Output_T, typename std::enable_if_t<std::numeric_limits<Output_T>::digits >= 8, int> = 0>
__attribute__((always_inline)) static inline
void compact_data_end_loop (Output_T* __restrict outputs,
                            int& outputOffset,
                            PackSupport& infoPack)
{
    //  Nothing
}



// ----------------------------------------------------------------------------
// ------------------------- Pooling subfunctions -----------------------------
// ------------------------------ Max Pooling ---------------------------------
// ----------------------------------------------------------------------------

__attribute__((always_inline)) static inline
int get_pool_nbData (const int nbBits)
{
    int nb_data = 1;
    switch (nbBits)
    {
    case 8: nb_data = 4;
            break;
    case 4: nb_data = 2;
            break;
    case 16: nb_data = 2;
            break;
    default:
        break;
    }
    return nb_data;
}

template<typename Output_T,
    typename std::enable_if<std::numeric_limits<Output_T>::digits == 4>::type* = nullptr>
__attribute__((always_inline)) static inline
void storeMaxPooling (Output_T* __restrict outputs,
                      int& outputOffset,
                      const uint32_t maxVal,
                      const int nb_data)
{
    uint32_t data_val = maxVal;
    assert(nb_data == 2 || nb_data == 1);

    // Gather bytes in pairs of bytes
    // Ex: 0x0A050403 -> 0x00A50043
    data_val = ((data_val & 0x0F000F00) >> 4) | (data_val & 0x000F000F);

    // Output compression and storage
    for (int index = 0; index < nb_data; ++index) {
        outputs[outputOffset] = (uint8_t) ((data_val >> 16*index) & 0xFF);
        outputOffset += 1;
    }
}

template<typename Output_T,
    typename std::enable_if<std::numeric_limits<Output_T>::digits == 8>::type* = nullptr>
__attribute__((always_inline)) static inline
void storeMaxPooling (Output_T* __restrict outputs,
                      int& outputOffset,
                      const uint32_t maxVal,
                      const int nb_data)
{
    memcpy(outputs, &maxVal, nb_data*sizeof(uint8_t));
}

template<typename Input_T,
         typename std::enable_if<(std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 16)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t& maxVal,
                         const int nb_data)
{
    assert(nb_data == 2 || nb_data == 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint16_t));

    maxVal = __UQSUB16(maxVal, in);
    maxVal = __UQADD16(maxVal, in);
}

template<typename Input_T,
         typename std::enable_if<(!std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 16)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t maxVal,
                         const int nb_data)
{
    assert(nb_data == 2 || nb_data == 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint16_t));

    maxVal = __SSUB16(maxVal, in);
    maxVal = __SEL(maxVal, 0);
    maxVal = __SADD16(maxVal, in);
}

template<typename Input_T,
         typename std::enable_if<(std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 8)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t& maxVal,
                         const int nb_data)
{
    assert(nb_data <= 4 && nb_data >= 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint8_t));

    maxVal = __UQSUB8(maxVal, in);
    maxVal = __UQADD8(maxVal, in);
}

template<typename Input_T,
         typename std::enable_if<(!std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 8)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t maxVal,
                         const int nb_data)
{
    assert(nb_data <= 4 && nb_data >= 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint8_t));

    maxVal = __SSUB8(maxVal, in);
    maxVal = __SEL(maxVal, 0);
    maxVal = __SADD8(maxVal, in);
}

template<typename Input_T,
         typename std::enable_if<(std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 4)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t& maxVal,
                         const int nb_data)
{
    assert(nb_data == 2 || nb_data == 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint8_t));

    in = (in | in << 8) & 0xFF00FF;
    in = (in | in << 4) & 0xF0F0F0F;

    maxVal = __UQSUB8(maxVal, in);
    maxVal = __UQADD8(maxVal, in);
}

template<typename Input_T,
         typename std::enable_if<(!std::is_unsigned<Input_T>::value
         && std::numeric_limits<Input_T>::digits == 4)>::type* = nullptr>
__attribute__((always_inline)) static inline
void parallelMaxPooling (const Input_T* __restrict inputs,
                         uint32_t maxVal,
                         const int nb_data)
{
    assert(nb_data == 2 || nb_data == 1);

    uint32_t in = 0;
    memcpy((void*) &in, inputs, nb_data*sizeof(uint8_t));

    in = (in | in << 8) & 0xFF00FF;
    in = (in | in << 4) & 0xF0F0F0F;
    in += 0x78787878;
    in ^= 0x78787878;

    maxVal = __SSUB8(maxVal, in);
    maxVal = __SEL(maxVal, 0);
    maxVal = __SADD8(maxVal, in);
}


#endif