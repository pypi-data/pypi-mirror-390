#include <iterator>

class Int8EntropyCalibrator : public nvinfer1::IInt8EntropyCalibrator2
{
public:
    Int8EntropyCalibrator(BatchStream& stream, int firstBatch, std::string cacheName, bool readCache = true)
        : _stream(stream),
          _calibrationCacheName(cacheName),
          _readCache(readCache)
    {
        nvinfer1::Dims dims = _stream.getDims();
        _inputCount = _stream.getBatchSize() * dims.d[1] * dims.d[2] * dims.d[3];
        CHECK_CUDA_STATUS(cudaMalloc(&_deviceInput, _inputCount * sizeof(float)));
        _stream.reset(firstBatch);
    }

    virtual ~Int8EntropyCalibrator()
    {
        CHECK_CUDA_STATUS(cudaFree(_deviceInput));
    }

    int getBatchSize() const noexcept override { return _stream.getBatchSize(); }

    bool getBatch(void* bindings[], const char* names[], int nbBindings) noexcept override
    {
        if (!_stream.next())
        {
            return false;
        }
        CHECK_CUDA_STATUS(cudaMemcpy(_deviceInput, _stream.getBatch(), _inputCount * sizeof(float), cudaMemcpyHostToDevice));
        bindings[0] = _deviceInput;
        return true;
    }

    const void* readCalibrationCache(size_t& length) noexcept override
    {
        _calibrationCache.clear();
        std::ifstream input(calibrationTableName(), std::ios::binary);
        input >> std::noskipws;
        if (_readCache && input.good())
        {
            std::copy(std::istream_iterator<char>(input), std::istream_iterator<char>(), std::back_inserter(_calibrationCache));
        }
        length = _calibrationCache.size();
        return length ? &_calibrationCache[0] : nullptr;
    }

    virtual void writeCalibrationCache(const void* cache, size_t length) noexcept override
    {
        std::ofstream output(calibrationTableName(), std::ios::binary);
        output.write(reinterpret_cast<const char*>(cache), length);
    }

private:
    std::string calibrationTableName()
    {
        return _calibrationCacheName;
    }
    BatchStream         _stream;
    size_t              _inputCount;
    bool                _readCache{true};
    std::string         _calibrationCacheName;
    void*               _deviceInput{nullptr};
    std::vector<char>   _calibrationCache;
};
