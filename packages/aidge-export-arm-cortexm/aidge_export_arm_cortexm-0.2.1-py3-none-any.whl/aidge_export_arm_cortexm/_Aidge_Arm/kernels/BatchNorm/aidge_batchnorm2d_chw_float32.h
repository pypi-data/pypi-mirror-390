#include <math.h>

void aidge_batchnorm2d_chw_float32 (const float* inputs,
                                    float* outputs,
                                    const float* input_mean,
                                    const float* input_var,
                                    const float* scale,
                                    const float* bias,
                                    float epsilon,
                                    int nb_channels,
                                    int channel_width,
                                    int channel_height)
{
    int featureMapSize = channel_width * channel_height;
    for (int ch = 0; ch < nb_channels; ++ch) 
    {
        int ioIndex = ch * featureMapSize;
        for (int i = ioIndex; i < ioIndex + featureMapSize; i++){
            outputs[i] = bias[ch];
        }
        float var =sqrt(input_var[ch] + epsilon);

        for (int feature = 0; feature<featureMapSize; ++feature) {
            outputs[ioIndex + feature] += scale[ch] * (inputs[ioIndex + feature]-input_mean[ch]) / var;
        }
    
    }
}