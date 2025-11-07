#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "Graph.hpp"

#include <vector>

namespace py = pybind11;


void init_Graph(py::module& m)
{
    py::enum_<ExecutionMode_T>(m, "exe_mode")
        .value("sync", ExecutionMode_T::SYNC)
        .value("async", ExecutionMode_T::ASYNC)
        .export_values()
        ;

    py::class_<Graph>(m, "Graph")
        .def(py::init<std::string, unsigned int, int>(), 
                py::arg("filepath") = "",
                py::arg("device_id") = 0, 
                py::arg("nb_bits") = -32,         
            R"mydelimiter(
        Construct a new Graph object.

        :param filepath: Path to the file to load (default is empty).
        :type filepath: str
        :param device_id: Device ID to use (default is 0).
        :type device_id: unsigned int
        :param nb_bits: Number of bits for data (default is -32).
        :type nb_bits: int
        )mydelimiter")
                
        .def("device", &Graph::device, py::arg("id"),  
            R"mydelimiter(
        Set the CUDA device.

        :param id: Device ID.
        :type id: unsigned int
        )mydelimiter")     
        
        .def("load", &Graph::load, py::arg("filepath"), 
            R"mydelimiter(
        Load a graph from a file, either a `.onnx` file or a `.trt` engine.

        :param filepath: Path to the file.
        :type filepath: str
        )mydelimiter")

        .def("save", &Graph::save, py::arg("filepath"), 
            R"mydelimiter(
        Save the current graph as a `.trt` engine.

        :param filepath: Path to the file.
        :type filepath: str
        )mydelimiter")

        .def("calibrate", &Graph::calibrate, py::arg("calibration_folder_path") = "./calibration_folder/", py::arg("cache_file_path") = "./calibration_cache", py::arg("batch_size") = 1, 
            R"mydelimiter(
        Calibrate the graph to determine the appropriate scaling factors for converting floating-point values to lower-precision representations, using the calibration data found inside the specified `calibration_folder`. This folder should include a `.info` file containing the dimensions of the calibration data, along with the data stored in a `.batch` file


        Calibration can be expensive, so it is beneficial to generate the calibration data once and then reuse it for subsequent builds of the network. The cache includes the regression cutoff and quantile values used to generate it, and will not be used if these do not match the settings of the current calibrator. However, the network should be recalibrated if its structure changes or if the input data set changes, and it is the responsibility of the application to ensure this.
        
        :param calibration_folder_path: Path to the calibration folder.
        :type calibration_folder_path: str
        :param cache_file_path: Path to the cache file.
        :type cache_file_path: str
        :param batch_size: Batch size for calibration (default is 1).
        :type batch_size: int
        )mydelimiter")

        .def("initialize", &Graph::initialize,
            R"mydelimiter(
        Initializes the TensorRT engine and execution context for the Graph class. This involves building a serialized network, deserializing it into a CUDA engine, and setting up the necessary execution context and I/O descriptors.
        )mydelimiter")

        .def("profile", &Graph::profile, py::arg("nb_iterations"), py::arg("mode")= ExecutionMode_T::ASYNC,
            R"mydelimiter(
        Profile the graph's execution by printing the average profiled TensorRT process time per stimulus.

        :param nb_iterations: Number of iterations for profiling.
        :type nb_iterations: unsigned int
        :param mode: Execution mode (SYNC or ASYNC, default is ASYNC).
        :type mode: ExecutionMode_T
        )mydelimiter")

        .def("run_sync", [](Graph& graph, py::list inputs) -> py::list {
            py::list outputs;
            std::vector<void *> bufferIn;
            std::vector<void *> bufferOut;

            IOGraphDesc iodesc = graph.getIODescription();

            // Fill bufferIn for inference
            for (py::handle array: inputs)
            {
                // py::buffer_info buf_info =
                //         array.cast<py::array_t<float>>().request();
                py::buffer_info buf_info = array.cast<py::array>().request();
                bufferIn.push_back(static_cast<void*>(buf_info.ptr));
            }

            // Allocate memory resources for bufferOut
            for (unsigned int i = 0; i < iodesc.outputs.size(); ++i)
            {
                void* out = (void *)new char[iodesc.outputs[i].size];
                bufferOut.push_back(out);
            }

            // Run inference
            graph.run_sync(bufferIn.data(), bufferOut.data());

            // Get outputs
            for (unsigned int i = 0; i < iodesc.outputs.size(); ++i)
            {
                // Improve the code by being independant from the type of output
                float* data_ptr = static_cast<float*>(bufferOut[i]);
                py::array_t<float> processed_array = py::array_t<float>(
                    iodesc.outputs[i].nbElements, data_ptr);
                outputs.append(processed_array);
            }
            return outputs;
        }, py::arg("inputs"),
            R"mydelimiter(
        Run the graph.

        :param inputs: Input data.
        :type inputs: list
        :param outputs: Output data.
        :type outputs: list
        :param mode: Execution mode (SYNC or ASYNC, default is ASYNC).
        :type mode: ExecutionMode_T
        )mydelimiter");
}

PYBIND11_MODULE(aidge_trt, m)
{
    init_Graph(m);
}
