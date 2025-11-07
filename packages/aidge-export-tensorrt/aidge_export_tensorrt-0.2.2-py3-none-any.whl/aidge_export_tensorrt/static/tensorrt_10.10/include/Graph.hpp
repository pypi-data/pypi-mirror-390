#ifndef __AIDGE_TENSORRT_GRAPH_HPP__
#define __AIDGE_TENSORRT_GRAPH_HPP__

#include "Utils.hpp"
#include "cuda_utils.h"
#include <string>
#include <vector>

#include <NvInfer.h>
#include <NvOnnxParser.h>

// Allow TensorRT to use up to 1GB of GPU memory for tactic selection
constexpr size_t MAX_WORKSPACE_SIZE = 1ULL << 30; // 1 GB

typedef enum
{
    SYNC,
    ASYNC
} ExecutionMode_T;

typedef struct
{
    std::string name;
    int nbElements;
    int size;
} IODesc;

typedef struct
{
    std::vector<IODesc> inputs;
    std::vector<IODesc> outputs;
    unsigned int nIO;
} IOGraphDesc;

/**
 * @class Graph
 * @brief Manages the lifecycle and execution of a neural network graph using TensorRT.
 *
 * The Graph class encapsulates the functionality required to manage, configure, and execute
 * a neural network graph for inference using NVIDIA's TensorRT. This includes loading models
 * from ONNX or TensorRT files, setting the CUDA device and data types, managing calibration
 * for INT8 precision, and running inference in both synchronous and asynchronous modes.
 */
class Graph
{
public:
    /**
     * @brief Constructor for the Graph class.
     *
     * @param filePath Path to the file to load (default is empty).
     * @param device_id Device ID to use (default is 0).
     * @param nbbits Number of bits for data (default is -32).
     */
    Graph(std::string const &filePath,
          unsigned int device_id,
          int nbbits);

    /**
     * @brief Destructor for the Graph class.
     */
    ~Graph();

    /**
     * @brief Set the CUDA device.
     *
     * @param id Device ID.
     */
    void device(unsigned int id);

    /**
     * @brief Set the data type for the graph.
     *
     * @param nbbits Number of bits for data.
     */
    void databits(int nbbits);

    /**
     * @brief Set the data mode for the graph.
     *
     * @param datatype Data type for the graph.
     */
    void datamode(nvinfer1::DataType datatype);

    /**
     * @brief Load a file into the graph.
     *
     * @param filePath Path to the file to load.
     */
    void load(std::string const &filePath);

    /**
     * @brief Load an ONNX file into the graph.
     *
     * @param onnxModelPath Path to the ONNX model file.
     */
    void load_onnx(std::string const &onnxModelPath);

    /**
     * @brief Load a TensorRT file into the graph.
     *
     * @param trtModelPath Path to the TensorRT model file.
     */
    void load_trt(std::string const &trtModelPath);

    /**
     * @brief Save the graph to a file.
     *
     * @param fileName Name of the file to save.
     */
    void save(std::string const &fileName);

    /**
     * @brief Initializes the TensorRT engine and execution context for the Graph class. This involves building a serialized network, deserializing it into a CUDA engine, and setting up the necessary execution context and I/O descriptors.
     */
    void initialize();

    /**
     * @brief Calibrate the graph using the calibration data found inside the `calibration` folder.
     * This folder should include a `.info` file containing the dimensions of the calibration data, along with the data stored in a `.batch` file*
     * Calibration can be expensive, so it is beneficial to generate the calibration data once and then reuse it for subsequent builds of the network. The cache includes the regression cutoff and quantile values used to generate it, and will not be used if these do not match the settings of the current calibrator. However, the network should be recalibrated if its structure changes or if the input data set changes, and it is the responsibility of the application to ensure this.
     *
     * @param calibration_folder_path Path to the calibration folder.
     * @param cache_file_path Path to the cache file.
     * @param batch_size Batch size for calibration (default is 1).
     */
    void calibrate(std::string const &calibration_folder_path, std::string const &cache_file_path, unsigned int batch_size);

    /**
     * @brief Profile the graph's execution by printing the average profiled tensorRT process time per stimulus.
     *
     * @param nb_iterations Number of iterations for profiling.
     * @param mode Execution mode (SYNC or ASYNC).
     */
    void profile(unsigned int nb_iterations, ExecutionMode_T mode = ExecutionMode_T::ASYNC);

    /**
     * @brief Automatically set the input profile for the graph.
     *
     * @param dims_inputs Dimensions of the input tensors.
     */
    void auto_input_profile(std::vector<std::vector<int>> dims_inputs);

    // Inference methods

    /**
     * @brief Run the graph.
     *
     * @param inputs Input data.
     * @param outputs Output data.
     * @param mode Execution mode (SYNC or ASYNC).
     */
    void run(void **inputs, void **outputs, ExecutionMode_T mode = ExecutionMode_T::ASYNC);

    /**
     * @brief Run the graph asynchronously.
     *
     * @param inputs Input data.
     * @param outputs Output data.
     */
    void run_async(void **inputs, void **outputs);

    /**
     * @brief Run the graph synchronously.
     *
     * @param inputs Input data.
     * @param outputs Output data.
     */
    void run_sync(void **inputs, void **outputs);

    // Getters

    /**
     * @brief Get the number of IO tensors in the graph.
     *
     * @return unsigned int Number of IO tensors.
     */
    unsigned int getNbIO();

    /**
     * @brief Get the IO descriptors of the graph.
     *
     * @return IOGraphDesc IO descriptors.
     */
    IOGraphDesc getIODescription();

protected:
    /**
     * @brief Initialize IO descriptors for the graph.
     */
    void initialize_io_descriptors();

private:
    // TensorRT objects for network, engine
    // and context creation and management
    nvinfer1::INetworkDefinition *_network{nullptr};
    nvinfer1::ICudaEngine *_engine{nullptr};
    nvinfer1::IBuilder *_builder{nullptr};
    nvinfer1::IBuilderConfig *_builderconfig{nullptr};
    nvinfer1::IExecutionContext *_context{nullptr};
    nvinfer1::IOptimizationProfile *_profile{nullptr};
    nvinfer1::IInt8Calibrator *_calibrator{nullptr};

    // Graph IO information
    IOGraphDesc _iodescriptors;
    // Buffer for GPU computation
    std::vector<void *> _iobuffer;
    // Stream
    cudaStream_t _stream{nullptr};
};

#endif // __AIDGE_TENSORRT_GRAPH_HPP__
