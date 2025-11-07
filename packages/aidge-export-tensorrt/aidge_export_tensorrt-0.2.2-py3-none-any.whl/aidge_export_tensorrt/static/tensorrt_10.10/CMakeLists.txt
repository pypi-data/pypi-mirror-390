cmake_minimum_required(VERSION 3.15)

# Options for compiling the export
option(PYBIND "python binding" ON)
option(TEST_DEBUG "c++ test for debugging" OFF)

# Define CMAKE constants
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_BUILD_TYPE_INIT Release)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Add cmake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake/")

project(Aidge_Export_TRT)
enable_language(CUDA)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} --compiler-options -fPIC")

# To remove override warnings by deprecated functions in plugin modules
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -diag-suppress 997")

add_library(aidge_trt_cpp STATIC)

# CUDAToolkit
if(${CMAKE_VERSION} VERSION_LESS "3.17.0")
    find_package(CUDAToolkit)
else()
    # For CMake >= 3.17.0, use the default FindCUDAToolkit provided by CMake
    # => in this case, we need to prevent find_package() to use our own.
    list(REMOVE_ITEM CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake/")
    find_package(CUDAToolkit)
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake/")
endif()

find_package(CuDNN)
find_package(TensorRT)

# Add include directory
target_include_directories(aidge_trt_cpp PUBLIC "include")

# Add plugin directory
target_include_directories(aidge_trt_cpp PUBLIC "plugins")

# Add cuda, cudnn and tensorrt include directories
target_include_directories(aidge_trt_cpp SYSTEM PUBLIC ${CUDAToolkit_INCLUDE_DIRS})
target_include_directories(aidge_trt_cpp SYSTEM PUBLIC ${CUDNN_INCLUDE_DIRS})
target_include_directories(aidge_trt_cpp SYSTEM PUBLIC ${TensorRT_INCLUDE_DIRS})

# Add cpp src files
file(GLOB_RECURSE cpp_src_files "src/*.cpp" "plugins/*.cpp")
target_sources(aidge_trt_cpp PUBLIC ${cpp_src_files})

# Add cuda src files
# Used PUBLIC for target sources in order to let tensorrt detect plugins
file(GLOB_RECURSE cuda_src_files "src/*.cu" "plugins/*.cu")
target_sources(aidge_trt_cpp PUBLIC ${cuda_src_files})

# Add libraries relative to CUDA
target_link_libraries(aidge_trt_cpp PUBLIC CUDA::cudart CUDA::cublas)

# Add libraries relative to CuDNN
target_link_libraries(aidge_trt_cpp PUBLIC ${CUDNN_LIBRARY})

# Add libraries relative to TensorRT
target_link_libraries(aidge_trt_cpp PUBLIC trt::nvinfer trt::nvonnxparser)

if (PYBIND)
    if(NOT EXISTS ${CMAKE_SOURCE_DIR}/python_binding/pybind11)
        message(STATUS "Folder python_binding/pybind 11 does not exist. Cloning from Git repository.")
        # Run the Git clone command
        execute_process(
            COMMAND git clone --depth=1 https://github.com/pybind/pybind11.git ${CMAKE_SOURCE_DIR}/python_binding/pybind11
            RESULT_VARIABLE git_clone_result
        )

        # Check the result of the Git clone operation
        if(git_clone_result)
            message(FATAL_ERROR "Failed to clone https://github.com/pybind/pybind11.git.\nError code: ${git_clone_result}")
        else()
            message(STATUS "Pybind11 cloned successfully.")
        endif()

        execute_process(
            COMMAND chmod -R a+w ${CMAKE_SOURCE_DIR}/python_binding/pybind11
        )
    endif()

    message(STATUS "Using python_binding/pybind11 for Python binding")
    add_subdirectory(${CMAKE_SOURCE_DIR}/python_binding/pybind11 ${CMAKE_BINARY_DIR}/pybind11)

    pybind11_add_module(aidge_trt MODULE "python_binding/pybind_export.cpp")
    target_include_directories(aidge_trt PUBLIC ${pybind11_INCLUDE_DIRS} "python_binding")
    target_link_libraries(aidge_trt PUBLIC aidge_trt_cpp)
endif()

if (TEST_DEBUG)
    add_executable(run_export "test_debug.cpp")
    target_link_libraries(run_export PUBLIC aidge_trt_cpp)
endif()
