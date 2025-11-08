if (NOT TARGET amulet_pybind11_extensions)
    set(amulet_pybind11_extensions_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")

    add_library(amulet_pybind11_extensions INTERFACE)
    target_include_directories(amulet_pybind11_extensions INTERFACE ${amulet_pybind11_extensions_INCLUDE_DIR})
endif()
