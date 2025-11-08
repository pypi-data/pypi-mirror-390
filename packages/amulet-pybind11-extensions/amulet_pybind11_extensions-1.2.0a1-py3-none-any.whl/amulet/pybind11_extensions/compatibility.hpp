#pragma once
#include <pybind11/pybind11.h>

#include <filesystem>
#include <string>

static std::string get_version_top(std::string version)
{
    return version.substr(0, version.find('.', version.find('.') + 1));
}

namespace Amulet {
namespace pybind11_extensions {

    inline void init_compiler_config(pybind11::module m)
    {
        pybind11::dict compiler_config;
        compiler_config["pybind11_version"] = PYBIND11_VERSION;
        compiler_config["compiler_id"] = COMPILER_ID;
        compiler_config["compiler_version"] = COMPILER_VERSION;
        m.attr("compiler_config") = compiler_config;
    }

    inline void check_compatibility(pybind11::module a, pybind11::module b)
    {
        std::string a_name = a.attr("__name__").cast<std::string>();
        std::string b_name = b.attr("__name__").cast<std::string>();
        pybind11::dict a_config = a.attr("compiler_config");
        pybind11::dict b_config = b.attr("compiler_config");

        std::string a_pybind11_version = a_config["pybind11_version"].cast<std::string>();
        std::string b_pybind11_version = b_config["pybind11_version"].cast<std::string>();
        if (a_pybind11_version != b_pybind11_version) {
            throw std::runtime_error(
                "pybind11 version mismatch. " + a_name + " is compiled for pybind11==" + a_pybind11_version + " and " + b_name + " is compiled for pybind11==" + b_pybind11_version);
        }

        std::string a_compiler_id = a_config["compiler_id"].cast<std::string>();
        std::string b_compiler_id = b_config["compiler_id"].cast<std::string>();
        if (a_compiler_id != b_compiler_id) {
            throw std::runtime_error(
                "compiler mismatch. " + a_name + " is compiled by " + a_compiler_id + " and " + b_name + " is compiled by " + b_compiler_id);
        }

        std::string a_compiler_version = a_config["compiler_version"].cast<std::string>();
        std::string b_compiler_version = b_config["compiler_version"].cast<std::string>();
        if (get_version_top(a_compiler_version) != get_version_top(b_compiler_version)) {
            throw std::runtime_error(
                "compiler version mismatch. " + a_name + " is compiled by " + a_compiler_id + " " + a_compiler_version + " and " + b_name + " is compiled by " + b_compiler_id + " " + b_compiler_version);
        }
    }

} // namespace pybind11_extensions
} // namespace Amulet
