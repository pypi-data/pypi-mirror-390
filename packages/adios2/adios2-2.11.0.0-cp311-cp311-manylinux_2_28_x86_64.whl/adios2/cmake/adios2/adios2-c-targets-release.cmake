#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "adios2::c" for configuration "Release"
set_property(TARGET adios2::c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(adios2::c PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "adios2::core"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/adios2/libadios2_c.so.2.11.0"
  IMPORTED_SONAME_RELEASE "libadios2_c.so.2.11"
  )

list(APPEND _cmake_import_check_targets adios2::c )
list(APPEND _cmake_import_check_files_for_adios2::c "${_IMPORT_PREFIX}/adios2/libadios2_c.so.2.11.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
