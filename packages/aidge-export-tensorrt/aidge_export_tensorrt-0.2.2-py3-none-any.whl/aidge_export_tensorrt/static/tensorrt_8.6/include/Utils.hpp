#ifndef __AIDGE_TENSORRT_UTILS_HPP__
#define __AIDGE_TENSORRT_UTILS_HPP__

#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <algorithm>
#include <NvInfer.h>
 
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



static void displayPlugins()
{
    int numCreators = 0;
    nvinfer1::IPluginCreator* const* tmpList = getPluginRegistry()->getPluginCreatorList(&numCreators);
    for (int k = 0; k < numCreators; ++k)
    {
        if (!tmpList[k])
            std::cout << "Plugin Creator for plugin " << k << " is a nullptr." << std::endl;
        else
            std::cout << k << ": " << tmpList[k]->getPluginName() << std::endl;
    }
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

#endif  // __AIDGE_TENSORRT_UTILS_HPP__