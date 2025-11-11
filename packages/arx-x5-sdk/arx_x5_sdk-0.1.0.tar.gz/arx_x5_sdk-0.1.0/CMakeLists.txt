cmake_minimum_required(VERSION 3.10)
project(arx_sdk VERSION 1.0)

# Find Python manually if executable is provided, before pybind11
if(PYTHON_EXECUTABLE)
    # Use the provided Python executable to find everything
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} -c "import sysconfig; print(sysconfig.get_path('include'))"
        OUTPUT_VARIABLE Python3_INCLUDE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))"
        OUTPUT_VARIABLE Python3_LIBRARY_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        OUTPUT_VARIABLE Python3_VERSION
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    set(Python3_EXECUTABLE ${PYTHON_EXECUTABLE})
    set(Python3_FOUND TRUE)
    set(Python3_Development_FOUND TRUE)
    set(Python3_Development_MODULE_FOUND TRUE)
    # Make sure pybind11 can find Python
    find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
endif()

find_package(pybind11 REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/lib/arx_x5_src/include)
include_directories(${PROJECT_SOURCE_DIR}/lib/arx_hardware_interface/include)

pybind11_add_module(${PROJECT_NAME} src/arx_x5_sdk.cpp)

if (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    message(STATUS "Target architecture is ARM")
    set(DEPEND_LIB "${CMAKE_CURRENT_SOURCE_DIR}/lib/arx_x5_src/libarx_x5_src-arm64.so")
else ()
    set(DEPEND_LIB "${CMAKE_CURRENT_SOURCE_DIR}/lib/arx_x5_src/libarx_x5_src.so")
endif ()

target_link_libraries(${PROJECT_NAME} PUBLIC ${DEPEND_LIB} pybind11::module)

# Set rpath so the library can be found in the same directory as the extension
# This allows the extension to find libarx_x5_src.so when installed
set_target_properties(${PROJECT_NAME} PROPERTIES
    INSTALL_RPATH "$ORIGIN"
    BUILD_WITH_INSTALL_RPATH TRUE
)

# Set installation path to the Python package directory
set(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/arx_x5_sdk/" CACHE PATH "Installation Directory" FORCE)

# Install the Python extension module
install(TARGETS ${PROJECT_NAME}
        LIBRARY DESTINATION .
        ARCHIVE DESTINATION .)

# Install the C++ library dependencies
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/lib/arx_x5_src/libarx_x5_src.so
        DESTINATION .)
if (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/lib/arx_x5_src/libarx_x5_src-arm64.so
            DESTINATION .)
