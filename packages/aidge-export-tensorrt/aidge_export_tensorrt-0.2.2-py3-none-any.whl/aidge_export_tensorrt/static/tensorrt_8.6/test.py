"""Example test file for the TensorRT Python API.
"""

# TODO Update the path to the shared object if needed
import build.lib.aidge_trt as aidge_trt
import numpy as np

if __name__ == '__main__':

    model = aidge_trt.Graph("model.onnx")

    model.initialize()

    # Profile with 10 iterations
    model.profile(10)

    # Execution example
    # img: numpy.array = np.load("PATH TO NPY file")
    # output: numpy.array = model.run_sync([img])

