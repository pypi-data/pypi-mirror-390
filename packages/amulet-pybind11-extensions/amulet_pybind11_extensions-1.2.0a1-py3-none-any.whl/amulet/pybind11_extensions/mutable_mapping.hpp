#pragma once
#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/collections.hpp>
#include <amulet/pybind11_extensions/mapping.hpp>
#include <amulet/pybind11_extensions/pybind11.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename KT, typename VT>
        class MutableMapping : public Mapping<KT, VT> {
        public:
            using Mapping<KT, VT>::Mapping;

            template <typename ClsT>
            static void def_pop(ClsT cls)
            {
                pybind11::object marker = pybind11::module::import("builtins").attr("Ellipsis");
                pybind11::options options;
                options.disable_function_signatures();
                cls.def(
                    "pop",
                    [marker](
                        pybind11::object self,
                        pybind11_extensions::PyObjectCpp<KT> key,
                        pybind11_extensions::PyObjectCpp<VT> default_) -> pybind11_extensions::PyObjectCpp<VT> {
                        pybind11::object value;
                        try {
                            value = self.attr("__getitem__")(key);
                        } catch (const pybind11::error_already_set& e) {
                            if (e.matches(PyExc_KeyError)) {
                                if (default_.is(marker)) {
                                    throw;
                                }
                                return default_;
                            } else {
                                throw;
                            }
                        }
                        self.attr("__delitem__")(key);
                        return value;
                    },
                    pybind11::doc((
                        std::string("pop(*args, **kwargs)\n")
                        + std::string("Overloaded function.\n")
                        + std::string("1. pop(self, key: ") + generate_arg_signature<KT>() + std::string(") -> ") + generate_return_signature<VT>() + std::string("\n")
                        + std::string("2. pop(self, key: ") + generate_arg_signature<KT>() + std::string(", default: ") + generate_return_signature<VT>() + std::string(") -> ") + generate_return_signature<VT>() + std::string("\n")
                        + std::string("3. pop[T](self, key: ") + generate_arg_signature<KT>() + std::string(", default: T) -> ") + generate_return_signature<VT>() + std::string(" | T\n"))
                            .c_str()),
                    pybind11::arg("key"),
                    pybind11::arg("default") = marker);
                options.enable_function_signatures();
            }

            template <typename ClsT>
            static void def_popitem(ClsT cls)
            {
                pybind11::object iter = pybind11::module::import("builtins").attr("iter");
                pybind11::object next = pybind11::module::import("builtins").attr("next");
                cls.def(
                    "popitem",
                    [iter, next](pybind11::object self) -> std::pair<
                                                            pybind11_extensions::PyObjectCpp<KT>,
                                                            pybind11_extensions::PyObjectCpp<VT>> {
                        pybind11::object key;
                        try {
                            key = next(iter(self));
                        } catch (const pybind11::error_already_set& e) {
                            if (e.matches(PyExc_StopIteration)) {
                                throw pybind11::key_error();
                            } else {
                                throw;
                            }
                        }
                        pybind11::object value = self.attr("__getitem__")(key);
                        self.attr("__delitem__")(key);
                        return std::make_pair(key, value);
                    });
            }

            template <typename ClsT>
            static void def_clear(ClsT cls)
            {
                cls.def(
                    "clear",
                    [](pybind11::object self) {
                        try {
                            while (true) {
                                self.attr("popitem")();
                            }
                        } catch (const pybind11::error_already_set& e) {
                            if (!e.matches(PyExc_KeyError)) {
                                throw;
                            }
                        }
                    });
            }

            template <typename ClsT>
            static void def_update(ClsT cls)
            {
                pybind11::object isinstance = pybind11::module::import("builtins").attr("isinstance");
                pybind11::object hasattr = pybind11::module::import("builtins").attr("hasattr");
                pybind11::object PyMapping = pybind11::module::import("collections.abc").attr("Mapping");
                cls.def(
                    "update",
                    [isinstance,
                        hasattr,
                        PyMapping](
                        pybind11::object self,
                        PyObjectCpp<std::variant<Mapping<KT, VT>, Iterable<pybind11::typing::Tuple<KT, VT>>>> other,
                        pybind11::KWArgs<VT> kwargs) {
                        if (pybind11::hasattr(other, "keys")) {
                            pybind11::object keys = other.attr("keys")();
                            for (auto it = keys.begin(); it != keys.end(); it++) {
                                self.attr("__setitem__")(*it, other.attr("__getitem__")(*it));
                            }
                        } else {
                            for (auto it = other.begin(); it != other.end(); it++) {
                                self.attr("__setitem__")(
                                    it->attr("__getitem__")(0),
                                    it->attr("__getitem__")(1));
                            }
                        }
                        pybind11::object items = kwargs.attr("items")();
                        for (auto it = items.begin(); it != items.end(); it++) {
                            self.attr("__setitem__")(
                                it->attr("__getitem__")(0),
                                it->attr("__getitem__")(1));
                        }
                    },
                    pybind11::arg("other") = pybind11::tuple());
            }

            template <typename ClsT>
            static void def_setdefault(ClsT cls, pybind11_extensions::PyObjectCpp<VT> default_value = pybind11::none())
            {
                pybind11::options options;
                options.disable_function_signatures();
                cls.def(
                    "setdefault",
                    [](
                        pybind11::object self,
                        pybind11_extensions::PyObjectCpp<KT> key,
                        pybind11_extensions::PyObjectCpp<VT> default_) -> pybind11::typing::Optional<VT> {
                        try {
                            return self.attr("__getitem__")(key);
                        } catch (const pybind11::error_already_set& e) {
                            if (e.matches(PyExc_KeyError)) {
                                self.attr("__setitem__")(key, default_);
                            } else {
                                throw;
                            }
                        }
                        return default_;
                    },
                    pybind11::doc((
                        std::string("setdefault(*args, **kwargs)\n")
                        + std::string("Overloaded function.\n")
                        + std::string("1. setdefault(self, key: ") + generate_arg_signature<KT>() + std::string(") -> ") + generate_return_signature<VT>() + std::string("\n")
                        + std::string("2. setdefault(self, key: ") + generate_arg_signature<KT>() + std::string(", default: ") + generate_arg_signature<VT>() + std::string(") -> ") + generate_return_signature<VT>() + std::string("\n"))
                            .c_str()),
                    pybind11::arg("key"),
                    pybind11::arg("default") = default_value);
                options.enable_function_signatures();
            }

            template <typename ClsT>
            static void register_cls(ClsT cls)
            {
                Mapping<KT, VT>::register_cls(cls);
                pybind11::module::import("collections.abc").attr("MutableMapping").attr("register")(cls);
            }
        };

        template <typename KT = pybind11::object, typename VT = pybind11::object, typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void def_MutableMapping_pop(ClsT cls)
        {
            MutableMapping<KT, VT>::def_pop(cls);
        }

        template <typename KT = pybind11::object, typename VT = pybind11::object, typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void def_MutableMapping_popitem(ClsT cls)
        {
            MutableMapping<KT, VT>::def_popitem(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void def_MutableMapping_clear(ClsT cls)
        {
            MutableMapping<pybind11::object, pybind11::object>::def_clear(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void def_MutableMapping_update(ClsT cls)
        {
            MutableMapping<pybind11::object, pybind11::object>::def_update(cls);
        }

        template <typename KT = pybind11::object, typename VT = pybind11::object, typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void def_MutableMapping_setdefault(ClsT cls)
        {
            MutableMapping<KT, VT>::def_setdefault(cls);
        }

        template <typename ClsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::MutableMapping")]]
        void register_MutableMapping(ClsT cls)
        {
            MutableMapping<pybind11::object, pybind11::object>::register_cls(cls);
        }

    } // namespace collections

    namespace detail {
        template <typename MapT>
        class MutableMapWrapper {
        public:
            using MapType = MapT;

            MapT& map;

            MutableMapWrapper(MapT& map)
                : map(map)
            {
            }
        };

        template <typename MapT, typename OwnerT>
        class OwningMutableMapWrapper : public MutableMapWrapper<MapT> {
        private:
            OwnerT owner;

        public:
            OwningMutableMapWrapper(MapT& map, OwnerT&& owner)
                : MutableMapWrapper<MapT>(map)
                , owner(std::forward<OwnerT>(owner))
            {
            }
        };

        template <typename MapWrapperT, typename ClsT>
        void bind_mutable_mapping_to(ClsT& cls)
        {
            using KT = typename MapWrapperT::MapType::key_type;
            using VT = typename MapWrapperT::MapType::mapped_type;
            bind_mapping_to<MapWrapperT>(cls);
            cls.def(
                "__setitem__",
                [](
                    MapWrapperT& self,
                    KT& key,
                    VT& value) {
                    self.map.insert_or_assign(key, value);
                });
            cls.def(
                "__delitem__",
                [](
                    MapWrapperT& self,
                    KT& key) {
                    self.map.erase(key);
                });
            cls.def(
                "clear",
                [](MapWrapperT& self) {
                    self.map.clear();
                });
            using MutableMapping = collections::MutableMapping<KT, VT>;
            MutableMapping::def_pop(cls);
            MutableMapping::def_popitem(cls);
            MutableMapping::def_update(cls);
            MutableMapping::def_setdefault(cls);
            MutableMapping::register_cls(cls);
        }

        template <typename MapWrapperT>
        void bind_mutable_mapping()
        {
            pybind11::class_<MapWrapperT> Mapping(pybind11::handle(), "MutableMapping", pybind11::module_local());
            bind_mutable_mapping_to<MapWrapperT>(Mapping);
        }
    }

    // Make a python class that models collections.abc.MutableMapping around a C++ map-like object.
    // The caller must tie the lifespan of the map to the lifespan of the returned object.
    template <typename MapT>
    collections::MutableMapping<typename MapT::key_type, typename MapT::mapped_type> make_mutable_mapping(MapT& map)
    {
        using MapWrapperT = detail::MutableMapWrapper<MapT>;
        if (!is_class_bound<MapWrapperT>()) {
            detail::bind_mutable_mapping<MapWrapperT>();
        }
        return pybind11::cast(MapWrapperT(map));
    }

    // Make a python class that models collections.abc.MutableMapping around a C++ map-like object.
    // Owner must keep the map alive until it is destroyed. It can be a smart pointer, pybind11::object or any object keeping the map alive.
    template <typename MapT, typename OwnerT>
    collections::MutableMapping<typename MapT::key_type, typename MapT::mapped_type> make_mutable_mapping(MapT& map, OwnerT&& owner)
    {
        using MapWrapperT = detail::OwningMutableMapWrapper<MapT, OwnerT>;
        if (!is_class_bound<MapWrapperT>()) {
            detail::bind_mutable_mapping<MapWrapperT>();
        }
        return pybind11::cast(MapWrapperT(map, std::forward<OwnerT>(owner)));
    }

} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename KT, typename VT>
    struct handle_type_name<Amulet::pybind11_extensions::collections::MutableMapping<KT, VT>> {
        static constexpr auto name = const_name("collections.abc.MutableMapping[") + return_descr(make_caster<KT>::name) + const_name(", ")
            + return_descr(make_caster<VT>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
