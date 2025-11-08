#pragma once
#include <amulet/pybind11_extensions/iterable.hpp>
#include <amulet/pybind11_extensions/iterator.hpp>
#include <amulet/pybind11_extensions/mapping.hpp>
#include <amulet/pybind11_extensions/mutable_mapping.hpp>
#include <amulet/pybind11_extensions/sequence.hpp>
#include <amulet/pybind11_extensions/mutable_sequence.hpp>

// I have found cases where I want to accept or return a python object matching a collections.abc class.
// This extension adds subclasses of pybind11::object with type hints for the collections.abc classes.
// This allows C++ functions to accept or return python objects that match the collection.abc classes.
// Note that these are handled in the same way as pybind11::object thus there is no type validation.
