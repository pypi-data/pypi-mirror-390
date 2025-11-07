#ifndef __AIDGE_SUPPORTFUNCTIONS_H__
#define __AIDGE_SUPPORTFUNCTIONS_H__

/**
 * @brief   Integer clamping
 * @param[in]  v   Value to be clamped
 * @param[in]  lo  Saturating lower bound
 * @param[in]  hi  Saturating higher bound
 * @returns        Value clamped between lo and hi
 * 
 */
static inline int clamp (int v, int lo, int hi) 
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
 * @brief   Maximum of two integer values
 */
static inline int max (int lhs, int rhs) 
{
    return (lhs >= rhs) ? lhs : rhs;
}

/**
 * @brief   Minimum of two integer values
 */
static inline int min (int lhs, int rhs) 
{
    return (lhs <= rhs) ? lhs : rhs;
}

#endif  // __AIDGE_SUPPORTFUNCTIONS_H__
