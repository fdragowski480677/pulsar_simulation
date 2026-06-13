cmake_minimum_required(VERSION 3.15)

project(p1dp
    VERSION 1.0
    LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

add_library(vectorSimLib STATIC
    src/Vector.cpp
    src/Simulation.cpp
)

target_include_directories(vectorSimLib
    PUBLIC
    ${PROJECT_SOURCE_DIR}/inc
)

add_executable(main
    src/main.cpp
)

target_link_libraries(main
    PRIVATE
    vectorSimLib
)
