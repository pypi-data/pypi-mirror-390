#include <cmath>

template <unsigned int SIZE, typename Input_T, typename Output_T>
__attribute__((always_inline)) inline static
void aidge_atan(Input_T* __restrict input, Output_T* __restrict output) {
  for (unsigned int i = 0; i < SIZE; ++i) {
    // Note : no cast to get compiler warning if we lose precision during auto cast!
    output[i] = std::atan(input[i]);
  }
}
