void aidge_slice_float32 (float* inputs,
                          float* outputs,
                          const int* axes,
                          const int* starts,
                          const int* ends,
                          unsigned int input_dims,
                          unsigned int nb_axes)
{
    // work only for one axe
    int out_index = 0;
    for (int i = starts[axes[0] - 1]; i < ends[axes[0] - 1]; ++i) {
        outputs[out_index++] = inputs[i];
    }
}
