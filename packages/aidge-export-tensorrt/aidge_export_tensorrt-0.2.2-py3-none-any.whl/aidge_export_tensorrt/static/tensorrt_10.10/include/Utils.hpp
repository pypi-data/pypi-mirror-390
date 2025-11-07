#ifndef __AIDGE_TENSORRT_UTILS_HPP__
#define __AIDGE_TENSORRT_UTILS_HPP__

#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <algorithm>
#include <NvInfer.h>
#include <cuda_runtime.h>
 
#define DIV_UP(X, Y) ((X) / (Y) + ((X) % (Y) > 0))
#define CEIL_DIV(X, Y) (((X) + (Y)-1) / (Y))


static struct Profiler : public nvinfer1::IProfiler
{
    typedef std::pair<std::string, float> Record;
    std::vector<Record> mProfile;

    virtual void reportLayerTime(const char* layerName, float ms) noexcept
    {
        auto record = std::find_if(mProfile.begin(), mProfile.end(), [&](const Record& r){ return r.first == layerName; });
        if (record == mProfile.end())
            mProfile.push_back(std::make_pair(layerName, ms));
        else
            record->second += ms;
    }

} gProfiler;

static class Logger : public nvinfer1::ILogger
{
    void log(Severity severity, const char* msg) noexcept override
    {
        switch (severity)
        {
        case Severity::kINTERNAL_ERROR:
            std::cerr << "INTERNAL_ERROR: ";
            break;
        case Severity::kERROR:
            std::cerr << "ERROR: ";
            break;
        case Severity::kWARNING:
            std::cerr << "WARNING: ";
            break;
        case Severity::kINFO:
            std::cerr << "INFO: ";
            break;
        default:
            std::cerr << "VERBOSE: ";
            break;
        }
        std::cerr << msg << std::endl;
    }
} gLogger;


static bool endsWith(std::string const &str, std::string const &suffix) 
{
    if (str.length() < suffix.length()) {
        return false;
    }
    return std::equal(suffix.rbegin(), suffix.rend(), str.rbegin());
}

static std::string removeSubstring(const std::string& input, const std::string& substringToRemove) {
    std::string result = input;
    size_t pos = result.find(substringToRemove);

    if (pos != std::string::npos) {
        result.erase(pos, substringToRemove.length());
    }

    return result;
}

static std::string baseName(const std::string& filePath)
{
    const size_t slashPos = filePath.find_last_of("/\\");
    return (slashPos == std::string::npos) ? filePath
                                           : filePath.substr(slashPos + 1);
}



static size_t dataTypeToSize(nvinfer1::DataType dataType)
{
    switch ((int)dataType) {
    case int(nvinfer1::DataType::kFLOAT):
        return 4;
    case int(nvinfer1::DataType::kHALF):
        return 2;
    case int(nvinfer1::DataType::kINT8):
        return 1;
    case int(nvinfer1::DataType::kINT32):
        return 4;
    case int(nvinfer1::DataType::kBOOL):
        return 1;
    default:
        return 4;
    }
}

static bool cudaSupportsDataType(nvinfer1::DataType dataType)
{
    int deviceId;
    cudaError_t status = cudaGetDevice(&deviceId);
    if (status != cudaSuccess) {
        std::cerr << "Failed to get CUDA device: " << cudaGetErrorString(status) << std::endl;
        return false;
    }

    cudaDeviceProp deviceProp;
    status = cudaGetDeviceProperties(&deviceProp, deviceId);
    if (status != cudaSuccess) {
        std::cerr << "Failed to get device properties: " << cudaGetErrorString(status) << std::endl;
        return false;
    }

    int major = deviceProp.major;
    int minor = deviceProp.minor;
    float computeCapability = major + minor * 0.1f;

    switch (dataType) {
        case nvinfer1::DataType::kFLOAT:
            // FP32 supported on all SM 7.5+
            return computeCapability >= 7.5f;
            
        case nvinfer1::DataType::kHALF:
            // FP16 supported on all SM 7.5+
            return computeCapability >= 7.5f;
            
        case nvinfer1::DataType::kINT8:
            // INT8 supported on all SM 7.5+
            return computeCapability >= 7.5f;

        case nvinfer1::DataType::kINT32:
            // INT32 supported on all SM 7.5+
            return computeCapability >= 7.5f;
            
        case nvinfer1::DataType::kBOOL:
            // BOOL supported on all SM 7.5+
            return computeCapability >= 7.5f;
        
        default:
            std::cerr << "Unknown data type in cudaSupportsDataType" << std::endl;
            return false;
    }
}

static bool cudaHasFastFp16()
{
    return cudaSupportsDataType(nvinfer1::DataType::kHALF);
}

static bool cudaHasFastInt8()
{
    return cudaSupportsDataType(nvinfer1::DataType::kINT8);
}

#endif  // __AIDGE_TENSORRT_UTILS_HPP__