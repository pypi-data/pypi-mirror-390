template <unsigned int SIZE, typename Input_T, typename Output_T>
__attribute__((always_inline)) inline static
void aidge_div(Input_T* __restrict input_a, Input_T* __restrict input_b, Output_T* __restrict output) {
  for (unsigned int i = 0; i < SIZE; ++i) {
      // Handle division by zero case
    if(input_b[i] != static_cast<Input_T>(0)) {
      output[i] = input_a[i] / input_b[i];
    } else {
      output[i] = static_cast<Output_T>(0); // or some other error handling ? 
    }
  }
}