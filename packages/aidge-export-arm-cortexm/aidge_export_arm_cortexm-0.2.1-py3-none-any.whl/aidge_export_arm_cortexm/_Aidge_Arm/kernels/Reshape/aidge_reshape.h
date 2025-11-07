#include <cstring>

template <unsigned int SIZE, typename T>
__attribute__((always_inline)) inline static
void aidge_reshape(T* __restrict input, T* __restrict output) {
    // Copy the input data to the output data
    std::memcpy(output, input, SIZE * sizeof(T));
}