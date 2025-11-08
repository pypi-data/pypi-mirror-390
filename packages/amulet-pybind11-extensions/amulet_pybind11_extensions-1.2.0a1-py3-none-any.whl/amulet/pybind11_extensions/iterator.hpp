#pragma once
#include <pybind11/pybind11.h>

#include <iterator>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/pybind11.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename T>
        class Iterator : public pybind11::object {
        public:
            PYBIND11_OBJECT_DEFAULT(Iterator, object, PyIter_Check)

            using iterator_category = std::input_iterator_tag;
            using difference_type = pybind11::ssize_t;
            using value_type = T;

            Iterator& operator++()
            {
                advance();
                return *this;
            }

            Iterator operator++(int)
            {
                auto rv = *this;
                advance();
                return rv;
            }

            T operator*() const
            {
                return obj().template cast<T>();
            }

            std::unique_ptr<T> operator->() const
            {
                return std::make_unique<T>(obj().template cast<T>());
            }

            static Iterator sentinel() { return {}; }

            friend bool operator==(const Iterator& a, const Iterator& b) { return a.obj().ptr() == b.obj().ptr(); }
            friend bool operator!=(const Iterator& a, const Iterator& b) { return a.obj().ptr() != b.obj().ptr(); }

        private:
            void advance()
            {
                value = pybind11::reinterpret_steal<pybind11::object>(PyIter_Next(m_ptr));
                if (value.ptr() == nullptr && PyErr_Occurred()) {
                    throw pybind11::error_already_set();
                }
            }

            const pybind11::object& obj() const
            {
                if (m_ptr && !value.ptr()) {
                    auto& self = const_cast<Iterator&>(*this);
                    self.advance();
                }
                return value;
            }

        private:
            pybind11::object value = {};
        };
        static_assert(std::input_iterator<Iterator<int>>);
    } // namespace collections

    // Create a python iterator around a C++ class that implements method next()
    // Next must throw pybind11::stop_iteration() to signal the end of the iterator.
    template <
        pybind11::return_value_policy Policy = pybind11::return_value_policy::automatic,
        typename It,
        typename... Extra>
    auto make_iterator(It it, Extra&&... extra) -> collections::Iterator<decltype(it.next())>
    {
        if (!is_class_bound<It>()) {
            pybind11::class_<It>(pybind11::handle(), "iterator", pybind11::module_local())
                .def(
                    "__iter__",
                    [](
                        PyObjectCpp<It>& self) -> PyObjectCpp<It>& { return self; })
                .def(
                    "__next__",
                    [](It& self) -> decltype(it.next()) {
                        return self.next();
                    },
                    std::forward<Extra>(extra)...,
                    Policy);
        }
        return pybind11::cast(std::forward<It>(it));
    }

} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T>
    struct handle_type_name<Amulet::pybind11_extensions::collections::Iterator<T>> {
        static constexpr auto name = const_name("collections.abc.Iterator[") + return_descr(make_caster<T>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
