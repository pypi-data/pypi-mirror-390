#ifndef __AIDGE_TENSORRT_CUDA_UTILS_H__
#define __AIDGE_TENSORRT_CUDA_UTILS_H__

#include <cublas_v2.h>
#include <cuda.h>
#include <cudnn.h>

#define FatalError(s)                                                          \
    {                                                                          \
        std::stringstream _where, _message;                                    \
        _where << __FILE__ << ':' << __LINE__;                                 \
        _message << std::string(s) + "\n" << __FILE__ << ':' << __LINE__;      \
        std::cerr << _message.str() << "\nAborting...\n";                      \
        cudaDeviceReset();                                                     \
        exit(EXIT_FAILURE);                                                    \
    }

#define CHECK_CUDA_STATUS(status)                                              \
    {                                                                          \
        std::stringstream _error;                                              \
        if (status != 0) {                                                     \
            _error << "Cuda failure: " << cudaGetErrorString(status);          \
            FatalError(_error.str());                                          \
        }                                                                      \
    }


#endif  // __AIDGE_TENSORRT_CUDA_UTILS_H__