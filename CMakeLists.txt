cmake_minimum_required(VERSION 3.5)

project(Raidionics)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/Raidionics")
set(EXTENSION_CATEGORY "AI")
set(EXTENSION_CONTRIBUTORS ", David Bouget (Medical Image Analysis group, Health Research Department, SINTEF Digital)")
set(EXTENSION_DESCRIPTION "Module for pre-/post-operative central nervous system tumor segmentation and standardized reporting")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/Raidionics.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Raidionics/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Raidionics)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
