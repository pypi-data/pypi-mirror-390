#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <algorithm>
#include <cstddef>
#include <memory>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/iterator.hpp>

namespace detail {
// An iterator for the collections.abc.Sequence protocol.
class SequenceIterator {
private:
    pybind11::object obj;
    size_t index;
    std::ptrdiff_t step;

public:
    SequenceIterator(
        pybind11::object obj,
        size_t start,
        std::ptrdiff_t step)
        : obj(obj)
        , index(start)
        , step(step)
    {
    }

    pybind11::object next()
    {
        if (index < 0 || pybind11::len(obj) <= index) {
            throw pybind11::stop_iteration("");
        }
        pybind11::object item = obj.attr("__getitem__")(index);
        index += step;
        return item;
    }
};
}

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename T>
        class Sequence : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(Sequence, object, PySequence_Check)

            Iterator<T> begin() const
            {
                return Iterator<T>(pybind11::object::begin());
            }

            Iterator<T> end() const
            {
                return Iterator<T>(pybind11::object::end());
            }

            Py_ssize_t size() const
            {
                return PyObject_Size(ptr());
            }

            template <typename ClsT>
            static void def_getitem_slice(ClsT cls)
            {
                cls.def(
                    "__getitem__",
                    [](pybind11::object self, const pybind11::slice& slice) -> pybind11::typing::List<T> {
                        size_t start = 0, stop = 0, step = 0, slicelength = 0;
                        if (!slice.compute(pybind11::len(self), &start, &stop, &step, &slicelength)) {
                            throw pybind11::error_already_set();
                        }
                        pybind11::list out(slicelength);
                        pybind11::object getitem = self.attr("__getitem__");
                        for (size_t i = 0; i < slicelength; ++i) {
                            out[i] = getitem(start);
                            start += step;
                        }
                        return out;
                    },
                    pybind11::arg("item"));
            }

            template <typename ClsT>
            static void def_contains(ClsT cls)
            {
                cls.def(
                    "__contains__",
                    [](pybind11::object self, pybind11::object value) {
                        pybind11::iterator it = pybind11::iter(self);
                        while (it != pybind11::iterator::sentinel()) {
                            if (it->equal(value)) {
                                return true;
                            }
                            ++it;
                        }
                        return false;
                    },
                    pybind11::arg("item"));
            }

            template <typename ClsT>
            static void def_iter(ClsT cls)
            {
                cls.def(
                    "__iter__",
                    [](pybind11::object self) -> pybind11_extensions::collections::Iterator<T> {
                        return Amulet::pybind11_extensions::make_iterator(::detail::SequenceIterator(self, 0, 1));
                    });
            }

            template <typename ClsT>
            static void def_reversed(ClsT cls)
            {
                cls.def(
                    "__reversed__",
                    [](pybind11::object self) -> pybind11_extensions::collections::Iterator<T> {
                        return Amulet::pybind11_extensions::make_iterator(::detail::SequenceIterator(self, pybind11::len(self) - 1, -1));
                    });
            }

            template <typename ClsT>
            static void def_index(ClsT cls)
            {
                cls.def(
                    "index",
                    [](pybind11::object self, PyObjectCpp<T> value, Py_ssize_t s_start, Py_ssize_t s_stop) {
                        size_t size = pybind11::len(self);
                        size_t start;
                        size_t stop;
                        if (s_start < 0) {
                            start = std::max<Py_ssize_t>(0, size + s_start);
                        } else {
                            start = s_start;
                        }
                        if (s_stop < 0) {
                            stop = size + s_stop;
                        } else {
                            stop = s_stop;
                        }
                        pybind11::object getitem = self.attr("__getitem__");
                        while (start < stop) {
                            pybind11::object obj;
                            try {
                                obj = getitem(start);
                            } catch (pybind11::error_already_set& e) {
                                if (e.matches(PyExc_IndexError)) {
                                    break;
                                } else {
                                    throw;
                                }
                            }

                            if (value.equal(obj)) {
                                return start;
                            }

                            start++;
                        }
                        throw pybind11::value_error("");
                    },
                    pybind11::arg("value"),
                    pybind11::arg("start") = 0,
                    pybind11::arg("stop") = std::numeric_limits<Py_ssize_t>::max());
            }

            template <typename ClsT>
            static void def_count(ClsT cls)
            {
                cls.def(
                    "count",
                    [](pybind11::object self, PyObjectCpp<T> value) {
                        size_t count = 0;
                        size_t size = pybind11::len(self);
                        pybind11::object getitem = self.attr("__getitem__");
                        for (size_t i = 0; i < size; ++i) {
                            if (value.equal(getitem(i))) {
                                count++;
                            }
                        }
                        return count;
                    },
                    pybind11::arg("value"));
            }

            template <typename ClsT>
            static void register_cls(ClsT cls)
            {
                pybind11::module::import("collections.abc").attr("Sequence").attr("register")(cls);
            }
        };

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_getitem_slice(ClsT cls)
        {
            Sequence<pybind11::object>::def_getitem_slice(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_contains(ClsT cls)
        {
            Sequence<pybind11::object>::def_contains(cls);
        }

        template <typename elemT = pybind11::object, typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_iter(ClsT cls)
        {
            Sequence<elemT>::def_iter(cls);
        }

        template <typename elemT = pybind11::object, typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_reversed(ClsT cls)
        {
            Sequence<elemT>::def_reversed(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_index(ClsT cls)
        {
            Sequence<pybind11::object>::def_index(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void def_Sequence_count(ClsT cls)
        {
            Sequence<pybind11::object>::def_count(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Sequence")]]
        void register_Sequence(ClsT cls)
        {
            Sequence<pybind11::object>::register_cls(cls);
        }
    } // namespace collections
} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T>
    struct handle_type_name<Amulet::pybind11_extensions::collections::Sequence<T>> {
        static constexpr auto name = const_name("collections.abc.Sequence[") + return_descr(make_caster<T>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
