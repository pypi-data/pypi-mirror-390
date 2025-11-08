#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <variant>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/hash.hpp>
#include <amulet/pybind11_extensions/iterator.hpp>
#include <amulet/pybind11_extensions/types.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace collections {
        template <typename KT>
        class KeysView : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(KeysView, object, PyObject_Type)
        };

        template <typename VT>
        class ValuesView : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(ValuesView, object, PyObject_Type)
        };

        template <typename KT, typename VT>
        class ItemsView : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(ItemsView, object, PyObject_Type)
        };

        template <typename KT, typename VT>
        class Mapping : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(Mapping, object, PyMapping_Check)

            template <typename ClsT>
            static void def_repr(ClsT cls)
            {
                cls.def(
                    "__repr__",
                    [](pybind11::object self) {
                        auto getitem = self.attr("__getitem__");
                        std::string repr = "{";
                        bool is_first = true;
                        for (auto it = self.begin(); it != self.end(); it++) {
                            if (is_first) {
                                is_first = false;
                            } else {
                                repr += ", ";
                            }
                            repr += pybind11::repr(*it);
                            repr += ": ";
                            repr += pybind11::repr(getitem(*it));
                        }
                        repr += "}";
                        return repr;
                    });
            }

            template <typename ClsT>
            static void def_contains(ClsT cls)
            {
                cls.def(
                    "__contains__",
                    [](pybind11::object self, pybind11_extensions::PyObjectCpp<KT> key) {
                        try {
                            self.attr("__getitem__")(key);
                            return true;
                        } catch (const pybind11::error_already_set& e) {
                            if (e.matches(PyExc_KeyError)) {
                                return false;
                            } else {
                                throw;
                            }
                        }
                    },
                    pybind11::arg("item"));
            }

            template <typename ClsT>
            static void def_keys(ClsT cls)
            {
                pybind11::object KeysView = pybind11::module::import("collections.abc").attr("KeysView");
                cls.def(
                    "keys",
                    [KeysView](pybind11::object self) -> pybind11_extensions::collections::KeysView<KT> { return KeysView(self); });
            }

            template <typename ClsT>
            static void def_values(ClsT cls)
            {
                pybind11::object ValuesView = pybind11::module::import("collections.abc").attr("ValuesView");
                cls.def(
                    "values",
                    [ValuesView](pybind11::object self) -> pybind11_extensions::collections::ValuesView<VT> { return ValuesView(self); });
            }

            template <typename ClsT>
            static void def_items(ClsT cls)
            {
                pybind11::object ItemsView = pybind11::module::import("collections.abc").attr("ItemsView");
                cls.def(
                    "items",
                    [ItemsView](pybind11::object self) -> pybind11_extensions::collections::ItemsView<KT, VT> { return ItemsView(self); });
            }

            template <typename ClsT>
            static void def_get(ClsT cls)
            {
                pybind11::options options;
                options.disable_function_signatures();
                cls.def(
                    "get",
                    [](
                        pybind11::object self,
                        pybind11_extensions::PyObjectCpp<KT> key,
                        pybind11_extensions::PyObjectCpp<VT> default_) -> pybind11_extensions::PyObjectCpp<VT> {
                        try {
                            return self.attr("__getitem__")(key);
                        } catch (const pybind11::error_already_set& e) {
                            if (e.matches(PyExc_KeyError)) {
                                return default_;
                            } else {
                                throw;
                            }
                        }
                    },
                    pybind11::doc((
                        std::string("get(*args, **kwargs)\n")
                        + std::string("Overloaded function.\n")
                        + std::string("1. get(self, key: ") + generate_arg_signature<KT>() + std::string(") -> ") + generate_return_signature<std::optional<VT>>() + std::string("\n")
                        + std::string("2. get(self, key: ") + generate_arg_signature<KT>() + std::string(", default: ") + generate_return_signature<VT>() + std::string(") -> ") + generate_return_signature<VT>() + std::string("\n")
                        + std::string("3. get[T](self, key: ") + generate_arg_signature<KT>() + std::string(", default: T) -> ") + generate_return_signature<VT>() + std::string(" | T\n"))
                            .c_str()),
                    pybind11::arg("key"),
                    pybind11::arg("default") = pybind11::none());
                options.enable_function_signatures();
            }

            template <typename ClsT>
            static void def_eq(ClsT cls)
            {
                pybind11::object dict = pybind11::module::import("builtins").attr("dict");
                pybind11::object isinstance = pybind11::module::import("builtins").attr("isinstance");
                pybind11::object NotImplemented = pybind11::module::import("builtins").attr("NotImplemented");
                pybind11::object PyMapping = pybind11::module::import("collections.abc").attr("Mapping");
                cls.def(
                    "__eq__",
                    [dict,
                        isinstance,
                        NotImplemented,
                        PyMapping](
                        pybind11::object self,
                        pybind11::object other) -> std::variant<bool, pybind11_extensions::types::NotImplementedType> {
                        if (!isinstance(other, PyMapping)) {
                            return NotImplemented;
                        }
                        return dict(self.attr("items")()).equal(dict(other.attr("items")()).cast<pybind11::dict>());
                    },
                    pybind11::arg("other"));
            }

            template <typename ClsT>
            static void def_hash(ClsT cls)
            {
                Amulet::pybind11_extensions::def_unhashable(cls);
            }

            template <typename ClsT>
            static void register_cls(ClsT cls)
            {
                pybind11::module::import("collections.abc").attr("Mapping").attr("register")(cls);
            }
        };

        template <typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_repr(clsT cls)
        {
            Mapping<pybind11::object, pybind11::object>::def_repr(cls);
        }

        template <typename KT = pybind11::object, typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_contains(clsT cls)
        {
            Mapping<KT, pybind11::object>::def_contains(cls);
        }

        template <typename KT = pybind11::object, typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_keys(clsT cls)
        {
            Mapping<KT, pybind11::object>::def_keys(cls);
        }

        template <typename VT = pybind11::object, typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_values(clsT cls)
        {
            Mapping<pybind11::object, VT>::def_values(cls);
        }

        template <typename KT = pybind11::object, typename VT = pybind11::object, typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_items(clsT cls)
        {
            Mapping<KT, VT>::def_items(cls);
        }

        template <typename KT = pybind11::object, typename VT = pybind11::object, typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_get(clsT cls)
        {
            Mapping<KT, VT>::def_get(cls);
        }

        template <typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_eq(clsT cls)
        {
            Mapping<pybind11::object, pybind11::object>::def_eq(cls);
        }

        template <typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void def_Mapping_hash(clsT cls)
        {
            Mapping<pybind11::object, pybind11::object>::def_hash(cls);
        }

        template <typename clsT>
        [[deprecated("Moved into Amulet::pybind11_extensions::collections::Mapping")]]
        void register_Mapping(clsT cls)
        {
            Mapping<pybind11::object, pybind11::object>::register_cls(cls);
        }

    } // namespace collections

    namespace detail {
        template <typename MapT>
        class MapWrapper {
        public:
            using MapType = MapT;

            const MapT& map;

            MapWrapper(const MapT& map)
                : map(map)
            {
            }
        };

        template <typename MapT, typename OwnerT>
        class OwningMapWrapper : public MapWrapper<MapT> {
        private:
            OwnerT owner;

        public:
            OwningMapWrapper(const MapT& map, OwnerT&& owner)
                : MapWrapper<MapT>(map)
                , owner(std::forward<OwnerT>(owner))
            {
            }
        };

        template <typename MapT>
        class MapIterator {
        private:
            const MapT& map;
            typename MapT::const_iterator begin;
            typename MapT::const_iterator end;
            typename MapT::const_iterator it;
            size_t size;

        public:
            MapIterator(const MapT& map)
                : map(map)
                , begin(map.begin())
                , end(map.end())
                , it(map.begin())
                , size(map.size())
            {
            }

            pybind11::object next()
            {
                // This is not fool proof.
                // There are cases where this is true but the iterator is invalid.
                // The programmer should write good code and this will catch some of the bad cases.
                if (size != map.size() || begin != map.begin() || end != map.end()) {
                    throw std::runtime_error("map changed size during iteration.");
                }
                if (it == end) {
                    throw pybind11::stop_iteration("");
                }
                return pybind11::cast((it++)->first);
            }
        };
    } // namespace detail

    // Make a collections.abc.Iterator around a C++ map-like object.
    // The caller must tie the lifespan of the map to the lifespan of the returned object.
    template <typename MapT>
    collections::Iterator<typename MapT::key_type> make_map_iterator(const MapT& map)
    {
        return make_iterator(detail::MapIterator(map));
    }

    namespace detail {
        template <typename MapWrapperT, typename ClsT>
        void bind_mapping_to(ClsT& cls)
        {
            using KT = typename MapWrapperT::MapType::key_type;
            using VT = typename MapWrapperT::MapType::mapped_type;
            cls.def(
                "__getitem__",
                [](MapWrapperT& self, pybind11::object key) {
                    try {
                        return pybind11::cast(self.map.at(key.cast<KT>()));
                    } catch (const std::out_of_range&) {
                        throw pybind11::key_error(pybind11::repr(key));
                    }
                });
            cls.def(
                "__iter__",
                [](MapWrapperT& self) {
                    return make_map_iterator(self.map);
                },
                pybind11::keep_alive<0, 1>());
            cls.def(
                "__len__",
                [](MapWrapperT& self) {
                    return self.map.size();
                });
            cls.def(
                "__contains__",
                [](MapWrapperT& self, pybind11::object key) {
                    return self.map.contains(key.cast<KT>());
                });
            using Mapping = collections::Mapping<KT, VT>;
            Mapping::def_repr(cls);
            Mapping::def_keys(cls);
            Mapping::def_values(cls);
            Mapping::def_items(cls);
            Mapping::def_get(cls);
            Mapping::def_eq(cls);
            Mapping::def_hash(cls);
            Mapping::register_cls(cls);
        }

        template <typename MapWrapperT>
        void bind_mapping()
        {
            pybind11::class_<MapWrapperT> Mapping(pybind11::handle(), "Mapping", pybind11::module_local());
            bind_mapping_to<MapWrapperT>(Mapping);
        }
    } // namespace detail

    // Make a python class that models collections.abc.Mapping around a C++ map-like object.
    // The caller must tie the lifespan of the map to the lifespan of the returned object.
    template <typename MapT>
    collections::Mapping<typename MapT::key_type, typename MapT::mapped_type> make_mapping(const MapT& map)
    {
        using MapWrapperT = detail::MapWrapper<MapT>;
        if (!is_class_bound<MapWrapperT>()) {
            detail::bind_mapping<MapWrapperT>();
        }
        return pybind11::cast(MapWrapperT(map));
    }

    // Make a python class that models collections.abc.Mapping around a C++ map-like object.
    // Owner must keep the map alive until it is destroyed. It can be a smart pointer, pybind11::object or any object keeping the map alive.
    template <typename MapT, typename OwnerT>
    collections::Mapping<typename MapT::key_type, typename MapT::mapped_type> make_mapping(const MapT& map, OwnerT&& owner)
    {
        using MapWrapperT = detail::OwningMapWrapper<MapT, OwnerT>;
        if (!is_class_bound<MapWrapperT>()) {
            detail::bind_mapping<MapWrapperT>();
        }
        return pybind11::cast(MapWrapperT(map, std::forward<OwnerT>(owner)));
    }

} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename KT>
    struct handle_type_name<Amulet::pybind11_extensions::collections::KeysView<KT>> {
        static constexpr auto name = const_name("collections.abc.KeysView[") + return_descr(make_caster<KT>::name) + const_name("]");
    };

    template <typename VT>
    struct handle_type_name<Amulet::pybind11_extensions::collections::ValuesView<VT>> {
        static constexpr auto name = const_name("collections.abc.ValuesView[") + return_descr(make_caster<VT>::name) + const_name("]");
    };

    template <typename KT, typename VT>
    struct handle_type_name<Amulet::pybind11_extensions::collections::ItemsView<KT, VT>> {
        static constexpr auto name = const_name("collections.abc.ItemsView[") + return_descr(make_caster<KT>::name) + const_name(", ")
            + return_descr(make_caster<VT>::name) + const_name("]");
    };

    template <typename KT, typename VT>
    struct handle_type_name<Amulet::pybind11_extensions::collections::Mapping<KT, VT>> {
        static constexpr auto name = const_name("collections.abc.Mapping[") + return_descr(make_caster<KT>::name) + const_name(", ") + return_descr(make_caster<VT>::name) + const_name("]");
    };
} // namespace detail
} // namespace pybind11
