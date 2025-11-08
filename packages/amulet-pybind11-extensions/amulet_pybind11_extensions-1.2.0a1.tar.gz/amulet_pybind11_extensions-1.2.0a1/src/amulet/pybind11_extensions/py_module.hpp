#pragma once
#include <pybind11/pybind11.h>

#include <filesystem>
#include <string>

namespace Amulet {
namespace pybind11_extensions {
    namespace detail {
        inline void def_package_path(pybind11::module m_parent, pybind11::module m, std::string name)
        {
            pybind11::list paths;
            pybind11::list parent_paths = m_parent.attr("__path__").cast<pybind11::list>();
            for (auto py_path : parent_paths) {
                if (pybind11::isinstance<pybind11::str>(py_path)) {
                    std::string path = py_path.cast<std::string>();
                    path.push_back(std::filesystem::path::preferred_separator);
                    path.append(name);
                    paths.append(pybind11::cast(path));
                }
            }
            m.attr("__path__") = paths;
        }
    }

    // pybind11 enables creation of sub-modules but not sub-packages.
    // This function creates a sub-module and defines __path__ to make it a package.
    // This enables importing from python modules within the package.
    inline pybind11::module def_subpackage(pybind11::module m_parent, std::string name)
    {
        auto m = m_parent.def_submodule(name.c_str());
        detail::def_package_path(m_parent, m, name);
        return m;
    }
} // namespace pybind11_extensions
} // namespace Amulet
