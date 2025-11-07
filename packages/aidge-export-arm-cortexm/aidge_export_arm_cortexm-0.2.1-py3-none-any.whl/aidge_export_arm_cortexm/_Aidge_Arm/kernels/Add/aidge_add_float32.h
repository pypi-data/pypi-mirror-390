void aidge_add_float32(const float* input_a,
                       const float* input_b,
                       float* output,
                       const int dim_a[],
                       const int dim_b[],
                       const int output_Dim[],
                       int size_dima,
                       int size_dimb,
                       int size_outputDim,
                       int output_size)
{
    // Broadcast dims
    int ndim_a[size_outputDim];
    int ndim_b[size_outputDim];

    for (int i= 0; i<size_outputDim; i++){
    	int idx = size_outputDim-size_dima;
    	ndim_a[i] = (i< idx) ? 1 : dim_a[i-idx];
    }


    for (int i= 0; i<size_outputDim; i++){
    	int idx = size_outputDim-size_dimb;
    	ndim_b[i] = (i< idx) ? 1 : dim_b[i-idx];
    }

    // Find the highest equal dimension
    int contiguousIdx = size_outputDim-1;
    while (ndim_a[contiguousIdx] == ndim_b[contiguousIdx]){
    	contiguousIdx--;
    }
    contiguousIdx++;

    // Compute the highest number of contiguous data for each Tensor
    int input0_contiguous_size = 1;
    for(int i = contiguousIdx; i<size_outputDim; ++i){
    	input0_contiguous_size *= ndim_a[i];
    }

    int input1_contiguous_size = 1;
    for(int i = contiguousIdx; i<size_outputDim; ++i){
    	input1_contiguous_size *= ndim_b[i];
    }

    int output_contiguous_size = 1;
    for(int i = contiguousIdx; i<size_outputDim; ++i){
    	output_contiguous_size *= output_Dim[i];
    }


    // initialize strides to iterate through data because of broadcasting
    int stride_post0[contiguousIdx] ;
    int stride_post1[contiguousIdx] ;
    int stride_step0[contiguousIdx] ;
    int stride_step1[contiguousIdx] ;
    if (contiguousIdx > 0) {
        stride_post0[contiguousIdx - 1] = 1;
        stride_post1[contiguousIdx - 1] = 1;
        for (int i = contiguousIdx-2; i != -1; --i) {
            stride_post0[i] = stride_post0[i+1]*ndim_a[i+1];
            stride_post1[i] = stride_post1[i+1]*ndim_b[i+1];
        }
        for (int i = 0; i < contiguousIdx; ++i) {
            stride_step0[i] = (ndim_a[i] == 1) ? 1 - stride_post0[i] : 1;
            stride_step1[i] = (ndim_b[i] == 1) ? 1 - stride_post1[i] : 1;
        }
    }

    int offsetIn0 = 0;
    int offsetIn1 = 0;
    int offsetOut = 0;
    int nbMatrices = 1;
    for(int i = 0; i<contiguousIdx; ++i){
        nbMatrices *= output_Dim[i];
    }
    int dim = contiguousIdx - 1;

    for(int stack = 0; stack < nbMatrices;){

    	for(int i = 0; i < output_contiguous_size; ++i){
    		int in0_id = (input0_contiguous_size != 1) ? i : 0;
    		int in1_id = (input1_contiguous_size != 1) ? i : 0;
    		output[i + offsetOut*output_contiguous_size] = input_a[in0_id + offsetIn0*input0_contiguous_size] + input_b[in1_id + offsetIn1*input1_contiguous_size];

    	}
        if (++stack < nbMatrices) {
            int tmp_stack = stack;
            while(tmp_stack % output_Dim[dim] == 0) {
                tmp_stack /= output_Dim[dim];
                dim--;
            }
            offsetIn0 += stride_step0[dim];
            offsetIn1 += stride_step1[dim];
            ++offsetOut;
            dim = contiguousIdx - 1;
        }

    }
}
