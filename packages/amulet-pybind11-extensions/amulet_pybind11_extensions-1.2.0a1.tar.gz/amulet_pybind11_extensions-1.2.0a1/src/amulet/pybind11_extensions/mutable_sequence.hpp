#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/iterable.hpp>
#include <amulet/pybind11_extensions/sequence.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename T>
        class MutableSequence : public Sequence<T> {
        public:
            using Sequence<T>::Sequence;

            template <typename ClsT>
            static void def_append(ClsT cls)
            {
                cls.def(
                    "append",
                    [](pybind11::object self, PyObjectCpp<T> value) {
                        self.attr("insert")(pybind11::len(self), value);
                    },
                    pybind11::arg("value"));
            }

            template <typename ClsT>
            static void def_clear(ClsT cls)
            {
                cls.def(
                    "clear",
                    [](pybind11::object self) {
                        try {
                            while (true) {
                                self.attr("pop")();
                            }
                        } catch (const pybind11::error_already_set& e) {
                            if (!e.matches(PyExc_IndexError)) {
                                throw;
                            }
                        }
                    });
            }

            template <typename ClsT>
            static void def_reverse(ClsT cls)
            {
                cls.def(
                    "reverse",
                    [](pybind11::object self) {
                        size_t l = pybind11::len(self);
                        size_t c = l / 2;
                        pybind11::object getitem = self.attr("__getitem__");
                        pybind11::object setitem = self.attr("__setitem__");
                        for (size_t i = 0; i < c; i++) {
                            auto a = getitem(i);
                            auto b = getitem(l - i - 1);
                            setitem(i, b);
                            setitem(l - i - 1, a);
                        }
                    });
            }

            template <typename ClsT>
            static void def_extend(ClsT cls)
            {
                // auto PyList = pybind11::module::import("builtins").attr("list");
                cls.def(
                    "extend",
                    [](pybind11::object self, pybind11::typing::Iterable<T> values) {
                        if (values.is(self)) {
                            values = pybind11::list(values);
                        }
                        auto append = self.attr("append");
                        for (auto value : values) {
                            append(value);
                        }
                    },
                    pybind11::arg("values"));
            }

            template <typename ClsT>
            static void def_pop(ClsT cls)
            {
                cls.def(
                    "pop",
                    [](pybind11::object self, Py_ssize_t index) {
                        auto value = self.attr("__getitem__")(index);
                        self.attr("__delitem__")(index);
                        return value;
                    },
                    pybind11::arg("index") = -1);
            }

            template <typename ClsT>
            static void def_remove(ClsT cls)
            {
                cls.def(
                    "remove",
                    [](pybind11::object self, PyObjectCpp<T> value) {
                        self.attr("__delitem__")(self.attr("index")(value));
                    },
                    pybind11::arg("value"));
            }

            template <typename ClsT>
            static void def_iadd(ClsT cls)
            {
                cls.def(
                    "__iadd__",
                    [](pybind11::object self, pybind11::typing::Iterable<T> values) {
                        self.attr("extend")(values);
                        return self;
                    },
                    pybind11::arg("values"));
            }

            template <typename ClsT>
            static void register_cls(ClsT cls)
            {
                Sequence<T>::register_cls(cls);
                pybind11::module::import("collections.abc").attr("MutableSequence").attr("register")(cls);
            }
        };
    } // namespace collections
} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T>
    struct handle_type_name<Amulet::pybind11_extensions::collections::MutableSequence<T>> {
        static constexpr auto name = const_name("collections.abc.MutableSequence[") + return_descr(make_caster<T>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
