#pragma once
#include <pybind11/pybind11.h>

#include <iterator>
#include <ranges>

#include <amulet/pybind11_extensions/iterator.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename T>
        class Iterable : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(Iterable, object, pybind11::detail::PyIterable_Check)

            Iterator<T> begin() const
            {
                return Iterator<T>(pybind11::object::begin());
            }
            Iterator<T> end() const
            {
                return Iterator<T>(pybind11::object::end());
            }
        };
        static_assert(std::ranges::input_range<Iterable<int>>);
        static_assert(std::convertible_to<std::ranges::range_value_t<Iterable<int>>, const int&>);
    } // namespace collections
} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T>
    struct handle_type_name<Amulet::pybind11_extensions::collections::Iterable<T>> {
        static constexpr auto name = const_name("collections.abc.Iterable[") + return_descr(make_caster<T>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
