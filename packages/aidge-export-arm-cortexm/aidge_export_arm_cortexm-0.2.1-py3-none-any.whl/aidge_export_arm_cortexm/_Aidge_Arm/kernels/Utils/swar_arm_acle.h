/**
 ******************************************************************************
 * @file     swar_arm_acle.h
 * @brief    Complete ARM Non-NEON ACLE intrinsics for Cortex m7 and m4
 * 
 ******************************************************************************
 * @attention
 * 
 * (C) Copyright 2021 CEA LIST. All Rights Reserved.
 *  Contributor(s): Vincent TEMPLIER (vincent.templier@cea.fr)
 *                  Philippe DORE (philippe.dore@cea.fr)
 * 
 * This file is not part of the open source version of N2D2 and is NOT under
 * the CeCILL-C license. This code is the property of the CEA. It can not be
 * copied or disseminated without its authorization.
 * 
 ******************************************************************************
 */

#ifndef _SWAR_ARM_ACLE_H
#define _SWAR_ARM_ACLE_H

#include <cmsis_compiler.h>
#include "assert.h"
#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief   Rotate right and perform dual extracted 8-bit to 16-bit signed addition
 * @details This function rotates op2, extracts two 8-bit values from op2 (at bit positions [7:0] and [23:16]), 
 *          sign-extend them to 16-bits each, and add the results to op1
 * @param[in]  op1  Two 16-bit values in op1[15:0] and op1[31:16]
 * @param[in]  op2  Two 8-bit values in op2[7:0] and op2[23:16] to be sign-extended
 * @param[in]  ror  Number of bits to rotate op2. Only 8,16 and 24 are accepted  
 * @returns         The addition of op1 and op2, where op2 has been rotated, the 8-bit values in op2[7:0] 
 *                  and op2[23:16] have been extracted and sign-extended prior to the addition
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
int32_t __SXTAB16_RORn (const int32_t op1, const int32_t op2, const int8_t ror)
{
    int32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("sxtab16 %0, %1, %2, ROR %3" : "=r" (result) : "r" (op1) , "r" (op2) , "i" (ror) );
    return result;
}


/**
 * @brief   Rotate right, dual extract 8-bits and sign extend each to 16-bits
 * @param[in]  op1  Two 8-bit values in op1[7:0] and op1[23:16] to be sign-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         The 8-bit values sign-extended to 16-bit values
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
int32_t __SXTB16_RORn (const int32_t op1, const int8_t ror)
{
    int32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("sxtb16 %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Rotate right and perform dual extracted 8-bit to 16-bit zero addition
 * @details This function rotates op2, extracts two 8-bit values from op2 (at bit positions [7:0] and [23:16]), 
 *          zero-extend them to 16-bits each, and add the results to op1
 * @param[in]  op1  Two 16-bit values in op1[15:0] and op1[31:16]
 * @param[in]  op2  Two 8-bit values in op2[7:0] and op2[23:16] to be zero-extended
 * @param[in]  ror  Number of bits to rotate op2. Only 8,16 and 24 are accepted  
 * @returns         The addition of op1 and op2, where op2 has been rotated, the 8-bit values in op2[7:0] 
 *                  and op2[23:16] have been extracted and zero-extended prior to the addition
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTAB16_RORn (const uint32_t op1, const uint32_t op2, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("uxtab16 %0, %1, %2, ROR %3" : "=r" (result) : "r" (op1) , "r" (op2) , "i" (ror) );
    return result;
}


/**
 * @brief   Rotate right, dual extract 8-bits and zero extend each to 16-bits
 * @param[in]  op1  Two 8-bit values in op1[7:0] and op1[23:16] to be zero-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         The 8-bit values zero-extended to 16-bit values
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTB16_RORn (const uint32_t op1, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("uxtb16 %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Sign extend Halfword
 * @details Extends a 16-bit value to a signed 32-bit value
 * @param[in]  op1  op1[15:0] to be sign-extended
 * @returns         Register holding the sign-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __SXTH (const uint32_t op1)
{
    uint32_t result;

    __ASM volatile ("sxth %0, %1" : "=r" (result) : "r" (op1));
    return result;
}


/**
 * @brief   Zero extend Halfword
 * @details Extends a 16-bit value to an unsigned 32-bit value
 * @param[in]  op1  op1[15:0] to be zero-extended
 * @returns         Register holding the zero-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTH (const uint32_t op1)
{
    uint32_t result;

    __ASM volatile ("uxth %0, %1" : "=r" (result) : "r" (op1));
    return result;
}


/**
 * @brief   Rotate right and sign extend halfword
 * @param[in]  op1  op1[15:0] to be sign-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         Register holding the sign-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __SXTH_RORn (const uint32_t op1, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("sxth %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Rotate right and zero extend halfword
 * @param[in]  op1  op1[15:0] to be zero-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         Register holding the zero-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTH_RORn (const uint32_t op1, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("uxth %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Sign extend Byte
 * @details Extends a 8-bit value to a signed 32-bit value
 * @param[in]  op1  op1[7:0] to be sign-extended
 * @returns         Register holding the sign-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __SXTB (const uint32_t op1)
{
    uint32_t result;

    __ASM volatile ("sxtb %0, %1" : "=r" (result) : "r" (op1));
    return result;
}


/**
 * @brief   Zero extend Byte
 * @details Extends a 8-bit value to an unsigned 32-bit value
 * @param[in]  op1  op1[7:0] to be zero-extended
 * @returns         Register holding the zero-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTB (const uint32_t op1)
{
    uint32_t result;

    __ASM volatile ("uxtb %0, %1" : "=r" (result) : "r" (op1));
    return result;
}


/**
 * @brief   Rotate right and sign extend byte
 * @param[in]  op1  op1[7:0] to be sign-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         Register holding the sign-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __SXTB_RORn (const uint32_t op1, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("sxtb %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Rotate right and zero extend byte
 * @param[in]  op1  op1[7:0] to be zero-extended
 * @param[in]  ror  Number of bits to rotate op1. Only 8,16 and 24 are accepted  
 * @returns         Register holding the zero-extended 32-bit value
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UXTB_RORn (const uint32_t op1, const int8_t ror)
{
    uint32_t result;

    assert((ror == 0) || (ror == 8) || (ror == 16) || (ror == 24));
    __ASM volatile ("uxtb %0, %1, ROR %2" : "=r" (result) : "r" (op1), "i" (ror) );
    return result;
}


/**
 * @brief   Signed Bit Field Extract
 * @details Copies adjacent bits from one register into the least significant bits 
 *          of a second register, and sign extends to 32 bits
 * @param[in]  op1    Value to be extracted
 * @param[in]  lsb    Position of the least significant bit of the bit field
 * @param[in]  width  Width of the bit field
 * @returns           Extracted bitfield and sign extended to 32 bits
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
int32_t __SBFX (const uint32_t op1, const int8_t lsb, const int8_t width)
{
    int32_t result;

    assert((lsb >= 0) && (lsb < 32) && (width >= 0) && (width < 32-lsb));
    __ASM volatile ("sbfx %0, %1, %2, %3" : "=r" (result) : "r" (op1), "i" (lsb), "i" (width) );
    return result;
}


/**
 * @brief   Unsigned Bit Field Extract
 * @details Copies adjacent bits from one register into the least significant bits 
 *          of a second register, and zero extends to 32 bits
 * @param[in]  op1    Value to be extracted
 * @param[in]  lsb    Position of the least significant bit of the bit field
 * @param[in]  width  Width of the bit field
 * @returns           Extracted bitfield and zero extended to 32 bits
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UBFX (const uint32_t op1, const int8_t lsb, const int8_t width)
{
    uint32_t result;

    assert((lsb >= 0) && (lsb < 32) && (width >= 0) && (width < 32-lsb));
    __ASM volatile ("ubfx %0, %1, %2, %3" : "=r" (result) : "r" (op1), "i" (lsb), "i" (width) );
    return result;
}


/**
 * @brief   Bit Field Insert
 * @details Copies a bitfield into one register from another register
 *          It replaces width bits in op2 starting at the position lsb, 
 *          with width bits from op1 starting at bit[0].  
 *          Other bits in op2 are unchanged
 * @param[in]      op1    Source value
 * @param[in,out]  op2    Destination value 
 * @param[in]      lsb    Position of the least significant bit of the bit field
 * @param[in]      width  Width of the bit field
 * @returns               The register which contains op2 and the added bitfield
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __BFI (uint32_t op1, uint32_t op2, const int8_t lsb, const int8_t width)
{
    assert((lsb >= 0) && (lsb < 32) && (width >= 0) && (width < 32-lsb));
    __ASM volatile ("bfi %0, %1, %2, %3" : "+r" (op2) : "r" (op1), "i" (lsb), "i" (width), "0" (op2) );
    return op2;
}


/**
 * @brief   Signed Divide
 * @details Performs a signed integer division of the value in op1 
 *          by the value in op2.
 * @param[in]  op1  Register holding the value to be divided
 * @param[in]  op2  Register holding the divisor
 * @returns         Register holding the signed result op1/op2
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __SDIV (const uint32_t op1, const uint32_t op2)
{
    uint32_t result;

    __ASM volatile ("sdiv %0, %1, %2" : "=r" (result) : "r" (op1), "r" (op2) );
    return result;
}


/**
 * @brief   Unsigned Divide
 * @details Performs an unsigned integer division of the value in op1 
 *          by the value in op2.
 * @param[in]  op1  Register holding the value to be divided
 * @param[in]  op2  Register holding the divisor
 * @returns         Register holding the unsigned result op1/op2
 * 
 */
__attribute__((always_inline)) __STATIC_INLINE 
uint32_t __UDIV (const uint32_t op1, const uint32_t op2)
{
    uint32_t result;

    __ASM volatile ("udiv %0, %1, %2" : "=r" (result) : "r" (op1), "r" (op2) );
    return result;
}


#ifdef __cplusplus
}
#endif

#endif

