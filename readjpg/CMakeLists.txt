include (CMakePrintHelpers)

cmake_minimum_required(VERSION 3.0)
project(ReadJPG)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)

# Find OpenCV package
find_package(OpenCV REQUIRED)

# Include directories
include_directories(${OpenCV_INCLUDE_DIRS})

cmake_print_variables(CMAKE_BUILD_TYPE)
#cmake_print_properties(
#        TARGETS read_jpg.o
#        PROPERTIES target_compile_options
#        )

# Add the executable target
add_executable(read_jpg read_jpg.cpp)
set_target_properties(read_jpg PROPERTIES ENABLE_EXPORTS TRUE)

# Link against OpenCV library
target_link_libraries(read_jpg ${OpenCV_LIBS})


