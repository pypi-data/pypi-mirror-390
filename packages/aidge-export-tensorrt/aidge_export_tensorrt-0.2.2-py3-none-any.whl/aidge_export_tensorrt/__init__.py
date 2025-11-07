from . import operators
from .operators import *

import os
import subprocess
import shutil
import aidge_onnx
import aidge_core
from jinja2 import Environment, FileSystemLoader

dirpath = os.path.dirname(__file__)

def generate_file(filename, templatename, **kwargs):

    # Get directory name of the file
    dirname = os.path.dirname(filename)

    # If directory doesn't exist, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Get directory name and name of the template
    template_dir = os.path.dirname(templatename)
    template_name = os.path.basename(templatename)

    # Select template
    template = Environment(loader=FileSystemLoader(template_dir)).get_template(template_name)

    # Generate file
    content = template.render(kwargs)
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)



def export(export_folder, graphview, python_binding=True, trt_version="10.10"):
    """Generate a TensorRT export.

    :param export_folder: Name of the folder where to generate the TensorRT export
    :type export_folder: str
    :param graphview: Graph description, can either be an Aidge graphview or a path to an ONNX file
    :type graphview: str or :py:class:`Aidge.GraphView`
    :param python_binding: If ``True``, clone PyBind into the export to enable python binding, defaults to True
    :type python_binding: bool, optional
    :param trt_version: The supported TensorRT version, defaults to "10.10"
    :type trt_version: str, optional
    """
    print(f"Generating TensorRT export in {export_folder}.")
    os.makedirs(export_folder, exist_ok=True)

    if isinstance(graphview, aidge_core.GraphView):
        aidge_onnx.export_onnx(graphview,
                            f"{export_folder}/model.onnx")
    elif isinstance(graphview, str):
        if graphview.endswith(".onnx"):
            shutil.copy(graphview, export_folder)
            # Rename onnx file to "model.onnx"
            _, old_name = os.path.split(graphview)
            os.rename(f"{export_folder}/{old_name}", f"{export_folder}/model.onnx")

        else:
            print("The file has to be an onnx file.")
    else:
        print("The model should be a GraphView or an onnx file.")

    shutil.copytree(f"{dirpath}/static/tensorrt_{trt_version}/",
                    export_folder,
                    dirs_exist_ok=True)
    if python_binding:
        print("Cloning PyBind11 inside export folder to enable Python binding ...")
        try:
            subprocess.run(["git", "clone",  "--depth=1", "https://github.com/pybind/pybind11.git", f"{export_folder}/python_binding/pybind11"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning PyBind11: {e}")
