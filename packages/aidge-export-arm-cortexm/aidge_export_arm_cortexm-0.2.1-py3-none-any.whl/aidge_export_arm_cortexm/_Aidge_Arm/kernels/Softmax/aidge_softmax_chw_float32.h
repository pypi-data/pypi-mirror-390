#include <math.h>

void aidge_softmax_chw_float32(const float* inputs,
                               float* outputs,
                               const int inputDims[],
                               int axis,
                               const unsigned int size_inputDim,
                               const unsigned int output_size)
{
    axis += (axis >= 0 ) ? 0 : size_inputDim;

    int postAxisElems = 1;
    for (unsigned int i = axis+1; i < size_inputDim; ++i) {
        postAxisElems *= inputDims[i];
    }
    int preAxisElems = 1;
    for (int i = 0; i < axis; ++i) {
        preAxisElems *= inputDims[i];
    }

    for (int i = 0; i < preAxisElems; ++i) {
        for (int j = 0; j < postAxisElems; ++j) {
            float sumExp = 0.0;
            for (int k = 0; k < inputDims[axis]; ++k) {
                int inIdx = i * inputDims[axis] * postAxisElems + k * postAxisElems + j;
                sumExp += exp(inputs[inIdx]);
            }
            for (int  k = 0; k < inputDims[axis]; ++k) {
                int inIdx = i * inputDims[axis] * postAxisElems + k * postAxisElems + j;
                outputs[inIdx] = exp(inputs[inIdx]) / sumExp;
            }
        }
    }
}
