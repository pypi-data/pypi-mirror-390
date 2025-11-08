#pragma once
#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/builtins.hpp>

// This extension adds a pybind11::object subclass for types.NotImplementedType.
// This is used as a return in comparison operators.

namespace Amulet {
namespace pybind11_extensions {
    namespace types {
        using NotImplementedType = pybind11_extensions::PyObjectStr<"types.NotImplementedType">;
    }
} // namespace pybind11_extensions
} // namespace Amulet
