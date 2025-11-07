#####################################################################
##: Different options to compile the export
##: Usage :
##:
##:    make / make help
##:         display the different options available
##:    make build_cpp
##:         compile the export on host for C++ apps
##:         (generate an executable in build/bin)
##:    make build_lib_python
##:         compile the export on host for Python apps
##:         (generate a python lib in build/lib)
##:    make build_image_docker
##:         generate the docker image of the tensorrt compiler
##:    make build_cpp_docker
##:         compile the export in a container for C++ apps
##:         (generate an executable in build/bin)
##:    make test_cpp_docker
##:         test the executable for C++ apps in a container
##:    make build_lib_python_docker
##:         compile the export in a container for Python apps
##:         (generate a python lib in build/lib)
##:    make test_lib_python_docker
##:         test the lib for Python apps in a container
##:    make clean
##:         clean up the build and bin folders
##:
#####################################################################

OBJDIR := build
BINDIR := bin
TARGET := ${BINDIR}/run_export
MAKEFLAGS := --no-print-directory
DOCKER_COMPILER := tools/tensorrt8.6_compiler.Dockerfile
IMAGE := tensorrt:8.6_compiler

all: help

.PHONY: build_cpp build_lib_python clean help

# Build for C++ app
build_cpp:
	./tools/compile_export_linux.sh -DPYBIND=0 -DTEST_DEBUG=1

# Build for Python app
build_lib_python:
	./tools/compile_export_linux.sh -DPYBIND=1 -DTEST_DEBUG=0

clean:
	if [ -d "$(OBJDIR)" ]; then rm -rf $(OBJDIR); fi
	if [ -d "$(BINDIR)" ]; then rm -rf $(BINDIR); fi

help:
	@grep -e "^##:"  Makefile;


# Makefile target for building the tensorrt compiler image
.PHONY: build_image_docker

build_image_docker:
	@docker build --pull --rm -f "${DOCKER_COMPILER}" -t ${IMAGE} tools/


# Makefile targets for building and testing c++ app via docker
.PHONY: build_cpp_docker test_cpp_docker

build_cpp_docker:
	@docker run --rm --name compiling -v "${PWD}":/usr/src/export -w /usr/src/export ${IMAGE} make build_cpp

test_cpp_docker:
	@docker run --rm --gpus=all --name testing -v "${PWD}":/usr/src/export -w /usr/src/export ${IMAGE} ./${OBJDIR}/${TARGET}


# Makefile targets for building and testing python app via docker
.PHONY: build_lib_python_docker test_lib_python_docker

build_lib_python_docker:
	@docker run --rm --name compiling -v "${PWD}":/usr/src/export -w /usr/src/export ${IMAGE} make build_lib_python

test_lib_python_docker:
	@docker run --rm --gpus=all --name testing -v "${PWD}":/usr/src/export -w /usr/src/export ${IMAGE} python3 test.py

