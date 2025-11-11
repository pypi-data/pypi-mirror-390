cmake_minimum_required(VERSION 3.10)

# Set policy to suppress warnings about install() destination normalization
if(POLICY CMP0177)
    cmake_policy(SET CMP0177 NEW)
endif()

project(arx_x5_sdk VERSION 1.0)

# Find pybind11 (handles Python detection automatically)
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

# Install the C++ library dependency (architecture-specific)
install(FILES ${DEPEND_LIB} DESTINATION .)
