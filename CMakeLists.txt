cmake_minimum_required(VERSION 3.27)
project(dummy_project_ai)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add source files
file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "src/*.h" "src/*.hpp")

# Create executable or library
if(SOURCES)
    add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})
    target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
else()
    message(STATUS "No source files found in src/ directory")
    # Create a minimal dummy target for testing the build
    add_library(${PROJECT_NAME} INTERFACE)
endif()

# Optional: Add tests if they exist
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/CMakeLists.txt")
    enable_testing()
    add_subdirectory(tests)
endif()
