cmake_minimum_required(VERSION 3.13)

######################
## Project settings ##
######################

project(Zamazenta
    VERSION "0.1.0"
    DESCRIPTION "Experimental decompilation of Pokémon Sword/Shield for Nintendo Switch"
    HOMEPAGE_URL "https://github.com/vbe0201/Zamazenta"
    LANGUAGES CXX
    )

#########################
## CMake configuration ##
#########################

# Set RelWithDebInfo as the default build type if nothing else has been chosen.
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING "Choose build type." FORCE)
endif()

# Configure the C++ environment for the project.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Nicely support folders in IDEs.
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

####################
## Subdirectories ##
####################

add_subdirectory(lib)
