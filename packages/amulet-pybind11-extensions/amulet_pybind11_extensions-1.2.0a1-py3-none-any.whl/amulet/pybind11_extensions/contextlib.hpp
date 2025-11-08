#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <functional>
#include <optional>
#include <type_traits>

#include <amulet/pybind11_extensions/pybind11.hpp>

namespace Amulet {
namespace pybind11_extensions {
    namespace contextlib {
        template <typename T, typename ExitT = std::optional<bool>>
        class ContextManager : public pybind11::object {
            PYBIND11_OBJECT_DEFAULT(ContextManager, object, PyObject_Type)
            using object::object;
        };

        namespace detail {
            template <typename T, typename ExitT = std::optional<bool>>
            class ContextManager {
            public:
                std::function<T()> enter;
                std::function<ExitT(pybind11::object, pybind11::object, pybind11::object)> exit;
                ContextManager(
                    std::function<T()> enter,
                    std::function<ExitT(pybind11::object, pybind11::object, pybind11::object)> exit)
                    : enter(enter)
                    , exit(exit)
                {
                }
            };
        }

        template <typename T, typename ExitT = std::optional<bool>>
        auto make_context_manager(
            std::function<T()> enter,
            std::function<ExitT(pybind11::object, pybind11::object, pybind11::object)> exit) -> ContextManager<T, ExitT>
        {
            using ContextManagerT = detail::ContextManager<T, ExitT>;
            if (!pybind11_extensions::is_class_bound<ContextManagerT>()) {
                pybind11::class_<ContextManagerT>(pybind11::handle(), "ContextManager", pybind11::module_local())
                    .def(
                        "__enter__",
                        [](const ContextManagerT& self) -> T {
                            return self.enter();
                        })
                    .def(
                        "__exit__",
                        [](const ContextManagerT& self, pybind11::object exc_type, pybind11::object exc_val, pybind11::object exc_tb) -> ExitT {
                            return self.exit(exc_type, exc_val, exc_tb);
                        });
            }
            return pybind11::cast(ContextManagerT(enter, exit));
        }
    } // namespace contextlib
} // namespace pybind11_extensions
} // namespace Amulet

namespace pybind11 {
namespace detail {
    template <typename T, typename ExitT>
    struct handle_type_name<Amulet::pybind11_extensions::contextlib::ContextManager<T, ExitT>> {
        static constexpr auto name = const_name("contextlib.AbstractContextManager[")
            + make_caster<std::conditional_t<std::is_same_v<void, T>, pybind11::none, T>>::name
            + const_name(", ") + make_caster<ExitT>::name + const_name("]");
    };
} // namespace detail
} // namespace pybind11
