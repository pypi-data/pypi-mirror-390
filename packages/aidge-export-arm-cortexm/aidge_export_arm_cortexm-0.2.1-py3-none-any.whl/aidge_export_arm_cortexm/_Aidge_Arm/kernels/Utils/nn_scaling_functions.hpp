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

#ifndef __NN_SCALING_FUNCTIONS_HPP__
#define __NN_SCALING_FUNCTIONS_HPP__

#include <stdint.h>
#include <stddef.h>
#include <cmath>

namespace N2D2_Export {

// static int64_t toInt64(uint32_t lo, uint32_t hi) {
//     return (int64_t) (((uint64_t) hi) << 32ull) | ((uint64_t) lo);
// }

// static int64_t smlal(int32_t lhs, int32_t rhs, 
//                      uint32_t accumLo, uint32_t accumHi) 
// {
//     return ((int64_t) lhs) * ((int64_t) rhs) + toInt64(accumLo, accumHi);
// }

// ---------------------------------------------------
// ------------------- No Scaling --------------------
// ---------------------------------------------------

struct NoScaling {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        return weightedSum;
    }

};

// ---------------------------------------------------
// ------------- Floating Point Scaling --------------
// ---------------------------------------------------

struct FloatingPointScaling {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        return round(weightedSum * mScaling);
    }

    // Scaling attribute
    double mScaling;
};

template<size_t SIZE>
struct FloatingPointClippingAndScaling {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        Sum_T clipValue = weightedSum;
        clipValue = (clipValue < Sum_T(0)) ?
                    Sum_T(0) : (clipValue > Sum_T(mClipping)) ?
                    Sum_T(mClipping) : clipValue;

        return round(clipValue * mScaling);
    }

    // Attributes
    double mScaling;
    int32_t mClipping;
};

template<size_t SIZE>
struct FloatingPointClippingAndScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        Sum_T clipValue = weightedSum;
        clipValue = (clipValue < Sum_T(0)) ? 
                    Sum_T(0) : (clipValue > Sum_T(mClipping[output])) ? 
                    Sum_T(mClipping[output]) : clipValue;

        return round(clipValue * mScaling[output]);
    }

    // Attributes
    double mScaling[SIZE];
    int32_t mClipping[SIZE];
};

template<size_t SIZE>
struct FloatingPointScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        return round(weightedSum * mScaling[output]);
    }

    // Scaling attribute
    double mScaling[SIZE];
};

// ---------------------------------------------------
// --------------- Fixed Point Scaling ---------------
// ---------------------------------------------------

template<int32_t SCALING, int64_t FRACTIONAL_BITS>
struct FixedPointScaling {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        return smlal(weightedSum, SCALING, HALF_LO, HALF_HI) >> FRACTIONAL_BITS; 
    }


    // Attributes
    static const uint32_t HALF_LO = (FRACTIONAL_BITS > 0)
        ? (1ull << (FRACTIONAL_BITS - 1)) & 0xFFFFFFFF : 0;
    static const uint32_t HALF_HI = (FRACTIONAL_BITS > 0)
        ? (1ull << (FRACTIONAL_BITS - 1)) >> 32u : 0;
    
    static const int32_t mScaling = SCALING;
    static const int64_t mFractionalBits = FRACTIONAL_BITS;
};

template<size_t SIZE, int64_t FRACTIONAL_BITS>
struct FixedPointClippingAndScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        Sum_T clipValue = weightedSum;
        clipValue = (clipValue < Sum_T(0)) ? 
                    Sum_T(0) : (clipValue > Sum_T(mClipping[output])) ? 
                    Sum_T(mClipping[output]) : clipValue;

        return smlal(clipValue, mScaling[output], HALF_LO, HALF_HI) >> FRACTIONAL_BITS; 
    }


    // Attributes
    static const uint32_t HALF_LO = (1ull << (FRACTIONAL_BITS - 1)) & 0xFFFFFFFF;
    static const uint32_t HALF_HI = (1ull << (FRACTIONAL_BITS - 1)) >> 32u;

    int32_t mScaling[SIZE];
    int32_t mClipping[SIZE];
};

template<size_t SIZE, int64_t FRACTIONAL_BITS>
struct FixedPointScalingScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        return smlal(weightedSum, mScaling[output], HALF_LO, HALF_HI) >> FRACTIONAL_BITS; 
    }


    // Attributes
    static const uint32_t HALF_LO = (FRACTIONAL_BITS > 0)
        ? (1ull << (FRACTIONAL_BITS - 1)) & 0xFFFFFFFF : 0;
    static const uint32_t HALF_HI = (FRACTIONAL_BITS > 0)
        ? (1ull << (FRACTIONAL_BITS - 1)) >> 32u : 0;

    int32_t mScaling[SIZE];
};

// ---------------------------------------------------
// --------------- Scaling by Shifting ---------------
// ---------------------------------------------------

template<int SHIFT>
struct SingleShiftScaling {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        return weightedSum >> SHIFT;
    }

    // Shift attribute
    static const int mShift = SHIFT;
};

template<size_t SIZE>
struct SingleShiftScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        return weightedSum >> mScaling[output];
    }

    // Scaling attributes
    unsigned char mScaling[SIZE];
};

template<int SHIFT1, int SHIFT2>
struct DoubleShiftScaling {
    
    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t /*output*/) const 
    {
        return (weightedSum + (weightedSum << SHIFT1) + (Sum_T)HALF) >> SHIFT2;
    }

    // Half value for rounding
    static const int HALF = 1 << (SHIFT2 - 1);
};

template<size_t SIZE, bool UNSIGNED_WEIGHTED_SUM>
struct DoubleShiftScalingPerChannel {

    template<typename Sum_T>
    Sum_T operator()(Sum_T weightedSum, size_t output) const 
    {
        const int SHIFT1 = mScaling[output][0];
        const int SHIFT2 = mScaling[output][1];
        const int HALF = mScaling[output][2];

        return (weightedSum + (weightedSum << SHIFT1) + (Sum_T)HALF) >> SHIFT2;
    }

    int mScaling[SIZE][3];
};


}   // N2D2_Export


#endif  // __NN_SCALING_FUNCTIONS_HPP__
