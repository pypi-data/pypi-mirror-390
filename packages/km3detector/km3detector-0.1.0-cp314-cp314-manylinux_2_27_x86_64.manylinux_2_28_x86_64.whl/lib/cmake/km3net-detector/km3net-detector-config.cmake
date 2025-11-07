include(CMakeFindDependencyMacro)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})





find_dependency(fmt)



find_dependency(nlohmann_json)


include(${CMAKE_CURRENT_LIST_DIR}/detector.cmake)
