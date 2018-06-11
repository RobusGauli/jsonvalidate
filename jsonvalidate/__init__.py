# -*- coding: utf-8 -*-

"""Top-level package for jsonvalidate."""

__author__ = """Robus Gauli"""
__email__ = 'robusgauli@gmail.com'
__version__ = '0.1.2'

from .jsonvalidate import (
    List,
    Object,
    NullContract,
    EnumContract,
    FloatContract,
    RangeContract,
    LengthContract,
    StringContract,
    IntegerContract,
    BooleanContract,
    KeyMissingContract,
)


__all__ = ['String', 'Integer', 'Float', 'Boolean', 'Object', 'List']


class String(KeyMissingContract, NullContract, StringContract, LengthContract, EnumContract):
    """Composition/Mixins for String"""
    pass


class Integer(KeyMissingContract, NullContract, IntegerContract, RangeContract, EnumContract):
    """Composition/Mixins for Integer"""
    pass


class Float(KeyMissingContract, NullContract, FloatContract, RangeContract, EnumContract):
    """Composition/Mixins for Float"""
    pass


class Boolean(KeyMissingContract, NullContract, BooleanContract):
    """Composition/Mixins for Boolean"""
    pass
