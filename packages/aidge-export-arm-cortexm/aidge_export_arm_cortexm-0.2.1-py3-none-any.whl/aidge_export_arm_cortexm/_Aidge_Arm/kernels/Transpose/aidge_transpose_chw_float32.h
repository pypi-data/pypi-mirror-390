void aidge_transpose_chw_float32 (const float* inputs,
                                  float* outputs,
                                  const int input_dims[],
                                  const int perm[],
                                  const int output_dims[],
                                  int size_outputDims,
                                  int output_size)
{
	int newStrides[size_outputDims];
	for (int i = 0; i < size_outputDims; ++i) {
        newStrides[i] = 1;
		for (int j = i + 1; j < size_outputDims; ++j) {
			newStrides[i] *= output_dims[j];
		}
	}

	int indices[size_outputDims];
	for (int i = 0; i < size_outputDims;++i){indices[i] = 0;}

	for (int i = 0; i < output_size; ++i) {
		int idx = 0;
		for (int j = size_outputDims -1; j >=0; --j) {
			idx += indices[perm[j]] * newStrides[j];
		}

		outputs[idx] = inputs[i];


		for (int j = size_outputDims - 1; j >= 0; --j) {
			if (indices[j] < input_dims[j] - 1) {
				indices[j]++;
				break;
			}
			else {
				indices[j] = 0;
			}
		}
	}
}
