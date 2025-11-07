

void aidge_sub_float32(const float* input_a,
                       const float* input_b,
                       float* output,
                       unsigned int size)
{
    for (unsigned int i = 0; i < size; ++i) {
        output[i] = input_a[i] - input_b[i];
    }
}
