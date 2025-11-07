void aidge_matmul_chw_float32(const float* input_a, 
                       const float* input_b, 
                       float* output,
                       const int dim_a[],
                       const int dim_b[],
                       const int output_Dim[],
                       const int size_dima,
                       const int size_dimb,
                       const int size_outputDim)
{
        //initialize arrays storing broadcasted(or not) dims
        int ndim_a[size_outputDim];     
        int ndim_b[size_outputDim];
        if ( size_dima == 1){ 
            ndim_a[0] = 1;
            ndim_a[1] = dim_a[0];
        }
        if ( size_dimb == 1){ 
            ndim_b[0] = dim_b[0];
            ndim_b[1] = 1;
        }
        
        for (int i= 0; i<size_outputDim; i++){
            int idx = size_outputDim-size_dima;
            ndim_a[i] = (i< idx) ? 1 : dim_a[i-idx];
        }


        for (int i= 0; i<size_outputDim; i++){
            int idx = size_outputDim-size_dimb;
            ndim_b[i] = (i< idx) ? 1 : dim_b[i-idx];
        }
        
    // initialize strides to iterate through data because of broadcasting
    int stride_post0[size_outputDim-2] ;
    int stride_post1[size_outputDim-2] ; 
    int stride_step0[size_outputDim-2] ;
    int stride_step1[size_outputDim-2] ; 
    if (size_outputDim > 2){ 
        stride_post0[size_outputDim - 3] = 1;
        stride_post1[size_outputDim - 3] = 1;
        for (int i = size_outputDim-4; i != -1; --i) {
            stride_post0[i] = stride_post0[i+1]*ndim_a[i+1];
            stride_post1[i] = stride_post1[i+1]*ndim_b[i+1];
        }
        for (int i = 0; i < size_outputDim-2; ++i) {
            stride_step0[i] = (ndim_a[i] == 1) ? 1 - stride_post0[i] : 1;
            stride_step1[i] = (ndim_b[i] == 1) ? 1 - stride_post1[i] : 1;
        }

    }

    
    // if size_dimb == size_dima, then size_dima == size_outputDim == size_dimb; 
    // else it will be broadcasted to the correct dims

    int nbMatrices = 1;
    for(int i = size_outputDim -3; i>=0; --i){
        nbMatrices *= output_Dim[i];
    }
    int dim = size_outputDim -3;


    int offsetIn0 = 0;
    int offsetIn1 = 0;
    int offsetOut = 0;
    const int n = ndim_a[size_outputDim - 2];
    const int k = ndim_a[size_outputDim - 1];
    const int m = ndim_b[size_outputDim - 1];
    const int matrix0Size = n*k;
    const int matrix1Size = k*m;
    const int matrixOutSize = n*m;

    for(int stack = 0; stack < nbMatrices;){
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                float sum = 0;
                for (int l = 0; l < k; ++l) {
                    sum += (input_a[ offsetIn0*matrix0Size + i*k + l] * input_b[offsetIn1*matrix1Size + l*m + j]);
                }
                output[ offsetOut*matrixOutSize + i*m + j] = sum;
            }
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
            dim = size_outputDim -3;
        }

    }

}