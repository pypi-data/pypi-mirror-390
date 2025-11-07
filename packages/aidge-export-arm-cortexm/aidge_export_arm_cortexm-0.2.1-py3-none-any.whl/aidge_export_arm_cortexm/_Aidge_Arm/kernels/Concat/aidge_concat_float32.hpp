template<typename T, unsigned int NB_INPUTS>
__attribute__((always_inline)) inline static
void aidge_concat(
    const unsigned int axis,
    const T* const * __restrict inputs,
    const unsigned int* __restrict sizes,
    T* __restrict output)
{
    unsigned int offset = 0;
    for (unsigned int n = 0; n < NB_INPUTS; ++n) {
        for (unsigned int i = 0; i < sizes[n]; ++i) {
            output[offset + i] = inputs[n][i];
        }
        offset += sizes[n];
    }
}
