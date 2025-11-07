#include <math.h>

template <unsigned int SIZE, typename Input_T, typename Output_T>
__attribute__((always_inline)) inline static
void aidge_sigmoid(Input_T* __restrict input, Output_T* __restrict output) {
    for (unsigned int i = 0; i < SIZE; ++i) {
        output[i] = 1 / ( 1 + exp(-input[i]) );
    }
}
