#include "Graph.hpp"
#include <fstream>
#include <sstream>
#include "BatchStream.hpp"
#include "IInt8EntropyCalibrator.hpp"
#include <dirent.h>

Graph::Graph( std::string const& filePath = "", 
              unsigned int device_id = 0, 
              int nbbits = -32)
{
    // ctor

    this->_builder = nvinfer1::createInferBuilder(gLogger);
    this->_profile = this->_builder->createOptimizationProfile();
    this->_builderconfig = this->_builder->createBuilderConfig();

    // this->_builderconfig->setMaxWorkspaceSize(MAX_WORKSPACE_SIZE);
    this->_builderconfig->setMemoryPoolLimit(nvinfer1::MemoryPoolType::kWORKSPACE, MAX_WORKSPACE_SIZE);

    CHECK_CUDA_STATUS(cudaStreamCreate(&(this->_stream)));

    device(device_id);
    databits(nbbits);

    if (!filePath.empty()) {
        load(filePath);
    }
}

Graph::~Graph()
{
    // dtor

    if (!this->_iobuffer.empty()) {
        for (unsigned int i = 0; i < this->_iobuffer.size(); ++i) {
            CHECK_CUDA_STATUS(cudaFree(this->_iobuffer[i]));
        }
        this->_iobuffer.clear();
    }

    CHECK_CUDA_STATUS(cudaStreamDestroy(this->_stream));
}

void Graph::device(unsigned int id)
{
    CHECK_CUDA_STATUS(cudaSetDevice(id));
}

void Graph::databits(int nbbits)
{
    nvinfer1::DataType datatype;

    if (nbbits == -32) {
        datatype = nvinfer1::DataType::kFLOAT;
    }
    else if (nbbits == -16) {
        datatype = nvinfer1::DataType::kHALF;
    }
    else if (nbbits == -8) {
        datatype = nvinfer1::DataType::kFP8;
    }
    else if (nbbits == 32) {
        datatype = nvinfer1::DataType::kINT32;
    }
    else if (nbbits == 8) {
        datatype = nvinfer1::DataType::kINT8;
    }
    else {
        std::cout << "Cannot use this number of bits ( "
                  << nbbits
                  << ") for infering the network"
                  << std::endl;
        return;
    }
    datamode(datatype);
}

void Graph::datamode(nvinfer1::DataType datatype)
{
    switch (datatype) {
        case nvinfer1::DataType::kFLOAT:
            // Do nothing as it is the default datatype
            break;

        case nvinfer1::DataType::kHALF: {
            if (!cudaHasFastFp16()) {
                std::cout << "Cannot use FP16 for this platform \nLet default datatype activated." << std::endl;
                return;
            }
            this->_builderconfig->setFlag(nvinfer1::BuilderFlag::kFP16);
        }
        break;

        case nvinfer1::DataType::kINT8: {
            if (!cudaHasFastInt8()) {
                std::cout << "Cannot use INT8 for this platform \nLet default datatype activated." << std::endl; 
                return;
            }
            
            // Mark calibrator as nullptr not to provide an INT8 calibrator
            this->_builderconfig->setFlag(nvinfer1::BuilderFlag::kINT8);   
        }
        break;

        case nvinfer1::DataType::kFP8:
        case nvinfer1::DataType::kINT32:
        case nvinfer1::DataType::kBOOL:
        case nvinfer1::DataType::kUINT8:
        default:
            std::cout << "Cannot use this datatype for infering the network \nLet default datatype activated." << std::endl;
            break;
    }
}

void Graph::calibrate(  std::string const& calibration_folder_path = "./calibration_folder/", 
                        std::string const& cache_file_path = "./calibration_cache",
                        unsigned int batch_size = 1)
{
    // Open calibration files 
    const std::string calibDir = calibration_folder_path;
    std::vector<std::string> filesCalib;
    struct dirent* pFile;
    DIR* pDir = opendir(calibDir.c_str());
    if (pDir == NULL) {
        std::cout << "No directory for batches calibration" << std::endl;
    }
    else {
        while ((pFile = readdir(pDir)) != NULL) 
        {
            if (pFile->d_name[0] != '.') filesCalib.push_back(std::string(calibDir + pFile->d_name));
        }
        closedir(pDir);
    }
    unsigned int nbCalibFiles = filesCalib.size();
    if(nbCalibFiles == 0) std::cout << "Cannot find calibration files in dir " << calibDir << std::endl;

    // Get input tensor shape by reading data.info file in calibration folder
    std::vector<unsigned int> dims;
    std::ifstream inputFile(calibDir + "/.info");
    if (!inputFile.is_open()) {
        std::cout << "Error opening the file .info" << std::endl;
    } else {
        std::string line;

        // Read all lines from the file
        while (std::getline(inputFile, line)) {
            try {
                unsigned int intValue = std::stoul(line); // Use stoul for unsigned int
                dims.push_back(intValue);
            } catch (const std::invalid_argument& e) {
                std::cerr << "Error converting string to unsigned int: " << e.what() << std::endl;
            } catch (const std::out_of_range& e) {
                std::cerr << "Error: Value out of range for unsigned int conversion." << std::endl;
            }
        }
    }
    inputFile.close();
    BatchStream calibrationStream(batch_size, dims, nbCalibFiles/batch_size, calibration_folder_path); 
    this->_calibrator = new Int8EntropyCalibrator(calibrationStream, 0, cache_file_path);
    this->_builderconfig->setInt8Calibrator(this->_calibrator);
}

void Graph::load(std::string const& filePath)
{
    if (endsWith(filePath, ".onnx")) {
        load_onnx(filePath);
    }
    else if (endsWith(filePath, ".trt")) {
        load_trt(filePath);
    }
    else {
        throw std::runtime_error("Cannot load this format of file");
    }
}


void Graph::load_onnx(std::string const& onnxModelPath)
{
    // Impose TensorRT flags for the creation of the network
    // Maybe change it to adapt graph to dynamic inputs
    nvinfer1::NetworkDefinitionCreationFlags creationFlag;
    creationFlag = 1 << static_cast<int32_t>(nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);

    this->_network = this->_builder->createNetworkV2(creationFlag);

    nvonnxparser::IParser* parser = nvonnxparser::createParser(*this->_network, gLogger);
    parser->parseFromFile(onnxModelPath.c_str(), static_cast<int>(nvinfer1::ILogger::Severity::kINFO));

    this->_network->setName(removeSubstring(baseName(onnxModelPath), ".onnx").c_str());
}

void Graph::load_trt(std::string const& trtModelPath)
{
    std::ifstream cudaEngineStream(trtModelPath);

    if(!cudaEngineStream.good())
        throw std::runtime_error("Could not open cuda engine file " + trtModelPath);

    nvinfer1::IRuntime* runtime = nvinfer1::createInferRuntime(gLogger);

    // Read the stringstream into a memory buffer and pass that to TRT
    cudaEngineStream.seekg(0, std::ios::end);
    const int modelSize = cudaEngineStream.tellg();
    cudaEngineStream.seekg(0, std::ios::beg);
    void* modelMem = malloc(modelSize);
    if(!modelMem)
        throw std::runtime_error("Could not allocate enough memory for load cuda engine file " + trtModelPath);

    cudaEngineStream.read((char*)modelMem, modelSize);

    this->_engine = runtime->deserializeCudaEngine(modelMem, modelSize);

    free(modelMem);
}

void Graph::save(std::string const& fileName)
{
    std::ofstream engineSerializedFile;

    nvinfer1::IHostMemory* memory = this->_engine->serialize();
    if (memory == nullptr)
        throw std::runtime_error("Serialize engine failed");

    // Open a new file
    engineSerializedFile.open(fileName + ".trt", std::ios::out | std::ios::binary);

    if (engineSerializedFile.is_open() && engineSerializedFile.good() && !engineSerializedFile.fail()) {
        //Save the serialized engine data into the file
        engineSerializedFile.write(reinterpret_cast<const char *>(memory->data()), memory->size());
        engineSerializedFile.close();
    }
    else
        throw std::runtime_error("Could not save cuda engine file in " + fileName + ".trt");
}

void Graph::initialize()
{
    if (!this->_engine) {
        nvinfer1::IHostMemory* engineString = this->_builder->buildSerializedNetwork(*(this->_network), *(this->_builderconfig));
        if (engineString == nullptr || engineString->size() == 0)
            throw std::runtime_error("Failed building serialized engine");

        nvinfer1::IRuntime* runtime = nvinfer1::createInferRuntime(gLogger);

        this->_engine = runtime->deserializeCudaEngine(engineString->data(), engineString->size());
    }
    this->_context = this->_engine->createExecutionContext();

    // Initialize IO information
    initialize_io_descriptors();
}

void Graph::auto_input_profile(std::vector<std::vector<int>> dims_inputs)
{
    // To improve by adding a system to read in a file/json the different optim and the dims
    for (int i = 0; i < this->_network->getNbInputs(); ++i) {
        nvinfer1::ITensor* input = this->_network->getInput(i);

        nvinfer1::Dims dims{};
        dims.nbDims = dims_inputs[i].size();
        for (unsigned int k = 0; k < dims_inputs[i].size(); ++k) {
            dims.d[k] = dims_inputs[i][k];
        }

        this->_profile->setDimensions(input->getName(), nvinfer1::OptProfileSelector::kMIN, dims);
        this->_profile->setDimensions(input->getName(), nvinfer1::OptProfileSelector::kOPT, dims);
        this->_profile->setDimensions(input->getName(), nvinfer1::OptProfileSelector::kMAX, dims);
    }

    this->_builderconfig->addOptimizationProfile(this->_profile);
}

void Graph::initialize_io_descriptors()
{
    this->_iodescriptors.nIO = this->_engine->getNbIOTensors();

    for (int nIO = 0; nIO < this->_engine->getNbIOTensors(); ++nIO) {
        std::string name = std::string(this->_engine->getIOTensorName(nIO));
        nvinfer1::Dims dim  = this->_context->getTensorShape(name.c_str());
        int size = 1;
        for (int j = 0; j < dim.nbDims; ++j) {
            size *= dim.d[j];
        }
        int datasize = size * dataTypeToSize(this->_engine->getTensorDataType(name.c_str()));

        IODesc descriptor {name, size, datasize};

        switch (this->_engine->getTensorIOMode(name.c_str())) {
            case nvinfer1::TensorIOMode::kINPUT:
                this->_iodescriptors.inputs.push_back(descriptor);
                break;

            case nvinfer1::TensorIOMode::kOUTPUT:
                this->_iodescriptors.outputs.push_back(descriptor);
                break;

            case nvinfer1::TensorIOMode::kNONE:
            default:
                break;
        }
    }
}

void Graph::run(void** inputs, void** outputs, ExecutionMode_T mode)
{
    switch (mode) {
        case SYNC: {
            run_sync(inputs, outputs);
            break;
        }
        case ASYNC: {
            run_async(inputs, outputs);
            break;
        }
        default:
            throw std::runtime_error("Running mode not supported");
    }
}

void Graph::run_async(void** inputs, void** outputs)
{
    unsigned int nbInputs = this->_iodescriptors.inputs.size();
    unsigned int nbOutputs = this->_iodescriptors.outputs.size();

    // Check if memory resources have been allocated for inputs and outputs
    // If not, allocate memory on device
    if (this->_iobuffer.empty()) {

        for (unsigned int i = 0; i < nbInputs; ++i) {
            void* inputPtr;
            CHECK_CUDA_STATUS(cudaMalloc(&inputPtr, this->_iodescriptors.inputs[i].size));
            this->_context->setTensorAddress(this->_iodescriptors.inputs[i].name.c_str(), inputPtr);
            this->_iobuffer.push_back(inputPtr);
        }

        for (unsigned int i = 0; i < nbOutputs; ++i) {
            void* outputPtr;
            CHECK_CUDA_STATUS(cudaMalloc(&outputPtr, this->_iodescriptors.outputs[i].size));
            this->_context->setTensorAddress(this->_iodescriptors.outputs[i].name.c_str(), outputPtr);
            this->_iobuffer.push_back(outputPtr);
        }

    }

    // Copy inputs to GPU
    for (unsigned int i = 0; i < nbInputs; ++i) {
        CHECK_CUDA_STATUS(cudaMemcpy(this->_iobuffer[i],
                                     inputs[i],
                                     this->_iodescriptors.inputs[i].size,
                                     cudaMemcpyHostToDevice));
    }

    // Run inference on GPU
   this->_context->enqueueV3(this->_stream);

    // Copy outputs to CPU
    for (unsigned int i = 0; i < nbOutputs; ++i) {
        CHECK_CUDA_STATUS(cudaMemcpy(outputs[i],
                                     this->_iobuffer[i + nbInputs],
                                     this->_iodescriptors.outputs[i].size,
                                     cudaMemcpyDeviceToHost));
    }
}

void Graph::run_sync(void** inputs, void** outputs)
{
    unsigned int nbInputs = this->_iodescriptors.inputs.size();
    unsigned int nbOutputs = this->_iodescriptors.outputs.size();

    // Check if memory resources have been allocated for inputs and outputs
    // If not, allocate memory on device
    if (this->_iobuffer.empty()) {

        for (unsigned int i = 0; i < nbInputs; ++i) {
            void* inputPtr;
            CHECK_CUDA_STATUS(cudaMalloc(&inputPtr, this->_iodescriptors.inputs[i].size));
            this->_iobuffer.push_back(inputPtr);
        }

        for (unsigned int i = 0; i < nbOutputs; ++i) {
            void* outputPtr;
            CHECK_CUDA_STATUS(cudaMalloc(&outputPtr, this->_iodescriptors.outputs[i].size));
            this->_iobuffer.push_back(outputPtr);
        }

    }

    // Copy inputs to GPU
    for (unsigned int i = 0; i < nbInputs; ++i) {
        CHECK_CUDA_STATUS(cudaMemcpy(this->_iobuffer[i],
                                     inputs[i],
                                     this->_iodescriptors.inputs[i].size,
                                     cudaMemcpyHostToDevice));
    }

    // Run inference on GPU
    this->_context->executeV2(this->_iobuffer.data());

    // Copy outputs to CPU
    for (unsigned int i = 0; i < nbOutputs; ++i) {
        CHECK_CUDA_STATUS(cudaMemcpy(outputs[i],
                                     this->_iobuffer[i + nbInputs],
                                     this->_iodescriptors.outputs[i].size,
                                     cudaMemcpyDeviceToHost));
    }
}

void Graph::profile(unsigned int nb_iterations, ExecutionMode_T mode)
{
    if(!this->_context) {
        throw std::runtime_error(
            "Cannot profile the graph without context from engine");
    }

    unsigned int nbInputs = this->_iodescriptors.inputs.size();
    unsigned int nbOutputs = this->_iodescriptors.outputs.size();

    // Initialize input buffer on CPU
    std::vector<void *> inputs {nbInputs, nullptr};
    for (unsigned int i = 0; i < nbInputs; ++i) {
        inputs[i] = (void *)new char[this->_iodescriptors.inputs[i].size];

        unsigned int nbElts = this->_iodescriptors.inputs[i].size / dataTypeToSize(this->_engine->getTensorDataType(this->_iodescriptors.inputs[i].name.c_str()));
        float *pData = (float *)inputs[i];
        for (unsigned int j = 0; j < nbElts; ++j) {
            pData[j] = float(j);
        }
    }

    // Initialize output buffer on CPU
    std::vector<void *> outputs {nbOutputs, nullptr};
    for (unsigned int i = 0; i < nbOutputs; ++i) {
        outputs[i] = (void *)new char[this->_iodescriptors.outputs[i].size];
    }

    // Run 1st inference to allocate GPU resources
    run(inputs.data(), outputs.data(), mode);

    this->_context->setProfiler(&gProfiler);

    for (unsigned int i = 0; i < nb_iterations; ++i) {
        run(inputs.data(), outputs.data(), mode);
    }

    double totalProcessTime = 0.0;

    for (size_t i = 0; i < gProfiler.mProfile.size(); ++i)
        totalProcessTime += gProfiler.mProfile[i].second / nb_iterations;

    for (size_t i = 0; i < gProfiler.mProfile.size(); i++)
    {
        const double processTimeMs = gProfiler.mProfile[i].second / nb_iterations;
        const double workLoad = (processTimeMs / totalProcessTime) * 100.0;
        std::string barrelLoad(((unsigned int)workLoad + 1) * 2, '*');
        std::cout << std::setprecision(10)
                  << "(" << std::setfill('0') << std::setw(2)
                  << (unsigned int)workLoad << "%)  " << barrelLoad
                  << "    " << gProfiler.mProfile[i].first << ": "
                  << processTimeMs << " ms"
                  << std::endl;
    }
    std::cout << "Average profiled tensorRT process time per stimulus = "
              << totalProcessTime <<  " ms" << std::endl;


    for (unsigned int i = 0; i < nbInputs; ++i) {
        delete[] (char *)inputs[i];
    }

    for (unsigned int i = 0; i < nbOutputs; ++i) {
        delete[] (char *)outputs[i];
    }

}

unsigned int Graph::getNbIO()
{
    return this->_iodescriptors.nIO;
}

IOGraphDesc Graph::getIODescription()
{
    return this->_iodescriptors;
}
