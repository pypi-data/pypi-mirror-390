void aidge_relu_float32 (const float* inputs,
                         float* outputs,
                         unsigned int size)
{
    for (unsigned int i = 0; i < size; ++i) {
        outputs[i] = (inputs[i] < 0.0f) ? 0.0f : inputs[i];
    }
}
