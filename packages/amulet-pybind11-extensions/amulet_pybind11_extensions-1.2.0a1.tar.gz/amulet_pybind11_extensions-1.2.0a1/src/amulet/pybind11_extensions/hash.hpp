#pragma once
#include <pybind11/pybind11.h>

namespace Amulet {
namespace pybind11_extensions {

    template <typename clsT>
    void def_hash_identity(clsT cls)
    {
        auto PyId = pybind11::module::import("builtins").attr("id");
        cls.def(
            "__hash__",
            [PyId](pybind11::object self) -> pybind11::int_ {
                return PyId(self);
            });
    }

    template <typename clsT>
    void def_unhashable(clsT cls)
    {
        auto cls_name = cls.attr("__name__").template cast<std::string>();
        cls.def(
            "__hash__",
            [cls_name](pybind11::object self) -> size_t {
                throw pybind11::type_error("unhashable type: '" + cls_name + "'");
            });
    }

} // namespace pybind11_extensions
} // namespace Amulet
