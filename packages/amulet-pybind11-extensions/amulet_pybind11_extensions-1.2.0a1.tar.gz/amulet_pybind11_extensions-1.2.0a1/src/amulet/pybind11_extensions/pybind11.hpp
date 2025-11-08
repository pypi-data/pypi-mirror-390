#pragma once
#include <pybind11/pybind11.h>

namespace Amulet {
namespace pybind11_extensions {
    inline void keep_alive(pybind11::handle nurse, pybind11::handle patient){
        pybind11::detail::keep_alive_impl(nurse, patient);
    }

    template <typename T>
    inline bool is_class_bound(){
        return pybind11::detail::get_type_info(typeid(T));
    }

    namespace detail {
        template <typename Descr>
        inline std::string generate_descriptor_signature(Descr descr)
        {
            static auto caster_name_field = descr;
            PYBIND11_DESCR_CONSTEXPR auto descr_types = decltype(caster_name_field)::types();
            // Create a default function_record to ensure the function signature has the proper
            // configuration e.g. no_convert.
            auto func_rec = pybind11::detail::function_record();
            size_t type_index = 0;
            size_t arg_index = 0;
            return generate_function_signature(
                caster_name_field.text, &func_rec, descr_types.data(), type_index, arg_index);
        }
    }

    template <typename T>
    inline std::string generate_signature()
    {
        return detail::generate_descriptor_signature(pybind11::detail::make_caster<T>::name);
    }

    template <typename T>
    inline std::string generate_arg_signature()
    {
        return generate_signature<T>();
    }

    template <typename T>
    inline std::string generate_return_signature()
    {
        return detail::generate_descriptor_signature(pybind11::detail::return_descr(pybind11::detail::make_caster<T>::name));
    }
} // namespace pybind11_extensions
} // namespace Amulet
