#pragma once
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

// The pybind11 type hint for array_t is incorrect
// This extension adds a subclass of array_t with the correct type hint.
// See pybind/pybind11/pull/5212

namespace Amulet {
namespace pybind11_extensions {
    namespace numpy {
        template <typename T, int ExtraFlags = pybind11::array::forcecast>
        class array_t : public pybind11::array_t<T, ExtraFlags> {
            using pybind11::array_t<T, ExtraFlags>::array_t;
        };
    }
} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T, int Flags>
    struct handle_type_name<Amulet::pybind11_extensions::numpy::array_t<T, Flags>> {
        static constexpr auto name
            = const_name("numpy.typing.NDArray[") + npy_format_descriptor<T>::name + const_name("]");
    };
} // namespace detail
} // namespace pybind11
