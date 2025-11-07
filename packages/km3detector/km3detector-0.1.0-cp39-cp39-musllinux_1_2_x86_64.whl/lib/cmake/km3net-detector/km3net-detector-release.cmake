#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "km3net::detector" for configuration "Release"
set_property(TARGET km3net::detector APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(km3net::detector PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libkm3net_detector.so"
  IMPORTED_SONAME_RELEASE "libkm3net_detector.so"
  )

list(APPEND _cmake_import_check_targets km3net::detector )
list(APPEND _cmake_import_check_files_for_km3net::detector "${_IMPORT_PREFIX}/lib/libkm3net_detector.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
