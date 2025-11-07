#include "Graph.hpp"
#include <iostream>
#include <vector>

// Uncomment if you want to run a single inference with static inputs
// #include "inputs.h"

int main()
{
    Graph model;

    model.load("model.onnx");

    // Uncomment if the model does not have explicit batch
    // Don't forget to change the values of the input dimensions
    // std::vector<std::vector<int>> dims_input{{ 1, 1, 28, 28 }}; 
    // model.auto_input_profile(dims_input);

    // Uncomment if you want to activate FP16
    // model.datamode(nvinfer1::DataType::kHALF);

    model.initialize();  

    // Comment to remove model profiling
    model.profile(10);


    // Example of script to run a single inference with static inputs

/*
    const unsigned int nb_classes = 10;

    std::vector<void *> bufferIn {1, nullptr};
    bufferIn[0] = (void *)inputs;

    std::vector<void *> bufferOut {1, nullptr};
    bufferOut[0] = (void *)new float[10];

    std::vector<void *> bufferIn {1, nullptr};
    bufferIn[0] = (void *)new char[28*28*1 * 4];
    float *pData = (float *)bufferIn[0];
    for (unsigned int j = 0; j < 784; ++j) {
        pData[j] = inputs[j];
    }

    std::vector<void *> bufferOut {1, nullptr};
    bufferOut[0] = (void *)new char[10 * 4];

    model.run_async(bufferIn.data(), bufferOut.data());

    float *floatArray = static_cast<float *>(bufferOut[0]);
    for (unsigned int i = 0; i < nb_classes; ++i)
    {
        std::cout << i << ": " << floatArray[i] << std::endl;
    }  

    delete[] (float *)bufferIn[0];
    delete[] (float *)bufferOut[0];
*/

    return 0;
}