cmake_minimum_required(VERSION 3.18...3.27)

project(camera_enum LANGUAGES CXX)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Create pybind11 extension module
pybind11_add_module(camera_enum src/cpp/camera_enum.cpp)

# Ensure proper Python extension naming
set_target_properties(camera_enum PROPERTIES
    PREFIX ""
    SUFFIX ".pyd"
)

install(TARGETS camera_enum LIBRARY DESTINATION camera_enum)
