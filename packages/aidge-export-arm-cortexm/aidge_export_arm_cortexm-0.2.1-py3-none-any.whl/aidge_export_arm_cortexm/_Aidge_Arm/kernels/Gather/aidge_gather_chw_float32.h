void aidge_gather_chw_float32 (const float* inputs,
                               float* outputs,
                               int axis,
                               const int indices[],
                               const int input_dims[],
                               int size_inputDim,
                               int indices_size,
                               int output_size)
{
	axis += (axis >= 0 ) ? 0 : size_inputDim;

    int postAxisElems = 1;
    for (int i = axis + 1; i < size_inputDim; ++i) {
        postAxisElems *= input_dims[i];
    }

    int preAxisElems = 1;
    for (int i = 0; i < axis; ++i) {
    	preAxisElems *= input_dims[i];
    }

      int outputOffset = 0;
    for (int i=0; i<preAxisElems; ++i){
        for(int j = 0; j< indices_size; j++){
            int idx = indices[j] >= 0 ?
                                        indices[j] :
                                        indices[j] + input_dims[axis];

            for(int k = 0; k<postAxisElems;++k){
            	int in_idx = i * postAxisElems * input_dims[axis] + idx * postAxisElems +k;
            	float tmp = inputs[in_idx];
                outputs[outputOffset + k] = tmp;
            }
            outputOffset += postAxisElems;
        }
    }
}