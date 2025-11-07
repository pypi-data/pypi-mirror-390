#ifndef BATCH_STREAM_H
#define BATCH_STREAM_H

#include "NvInfer.h"
#include <algorithm>
#include <assert.h>
#include <stdio.h>
#include <vector>

class BatchStream
{
public:
    BatchStream(unsigned int batchSize, std::vector<unsigned int> dims, unsigned int maxBatches, std::string prefix)
        : _batchSize(batchSize)
        , _maxBatches(maxBatches)
        , _prefix(prefix)
    {
        _dims.nbDims = dims.size()+1;  //The number of dimensions. Max 8.
        assert(_dims.nbDims <= 8 && "The maximum number of dimensions supported for a tensor is 8");
        _dims.d[0] = batchSize;    //Batch Size

        for(std::size_t i = 0; i < _dims.nbDims-1; ++i) _dims.d[i+1] = dims[i];
        for(auto elem : dims) _imageSize *= elem;
        _batch.resize(_batchSize * _imageSize, 0);
        _fileBatch.resize(_dims.d[0] * _imageSize, 0);
        reset(0);
    }

    // Resets data members
    void reset(int firstBatch)
    {
        _batchCount = 0;
        _fileCount = 0;
        _fileBatchPos = _dims.d[0];
        skip(firstBatch);
    }

    // Advance to next batch and return true, or return false if there is no batch left.
    bool next()
    {
        if (_batchCount == _maxBatches)
            return false;

        for (int csize = 1, batchPos = 0; batchPos < _batchSize; batchPos += csize, _fileBatchPos += csize)
        {
            assert(_fileBatchPos > 0 && _fileBatchPos <= _dims.d[0]);
            if (_fileBatchPos == _dims.d[0] && !update())
                return false;

            // copy the smaller of: elements left to fulfill the request, or elements left in the file buffer.
            csize = std::min(_batchSize - batchPos, static_cast<int32_t>(_dims.d[0] - _fileBatchPos));
            std::copy_n(getFileBatch() + _fileBatchPos * _imageSize, csize * _imageSize, getBatch() + batchPos * _imageSize);
        }
        _batchCount++;
        return true;
    }

    // Skips the batches
    void skip(int skipCount)
    {
        if (_batchSize >= _dims.d[0] && _batchSize % _dims.d[0] == 0 && _fileBatchPos == _dims.d[0])
        {
            _fileCount += skipCount * _batchSize / _dims.d[0];
            return;
        }

        int x = _batchCount;
        for (std::size_t i = 0; i < skipCount; ++i) next();
        _batchCount = x;
    }

    float* getBatch() { return &_batch[0]; }
    int getBatchesRead() const { return _batchCount; }
    int getBatchSize() const { return _batchSize; }
    int getImageSize() const { return _imageSize; }
    nvinfer1::Dims getDims() const { return _dims; }

private:
    float* getFileBatch() { return &_fileBatch[0]; }

bool update()
{
    std::string inputFileName = _prefix + std::to_string(_fileCount++) + ".batch";
    std::ifstream file(inputFileName, std::ios_base::in);
 
    if (!file.is_open()) std::cout << "Could not open calibration file " << inputFileName << std::endl;
    for(std::size_t i = 0; i < _imageSize; ++i) 
    {
        if(file.eof()) 
        {
            std::cerr << "Error: Unexpected end of file. Wrong input size." << std::endl;
            std::exit(EXIT_FAILURE);
        }
        file >> _fileBatch[i];
    }
    _fileBatchPos = 0;

    file.close();
    return true;
}

    int                 _batchSize{0};
    int                 _maxBatches{0};
    int                 _batchCount{0};
    int                 _fileCount{0};
    int                 _fileBatchPos{0};
    int                 _imageSize{1};
    nvinfer1::Dims      _dims;
    std::vector<float>  _batch;
    std::vector<float>  _fileBatch;
    std::string         _prefix;
};
#endif
