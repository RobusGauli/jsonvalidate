"""
    jsonvalidate.error
    ~~~~~~~~~~~~~~~~~~
    This module defines possible error types for json validation schema.
"""
# ERROR TYPES CONSTANTS
TYPE_ERROR = 'type_error'
NULL_ERROR = 'null_error'
KEY_MISSING_ERROR = 'key_missing_error'
RANGE_ERROR = 'range_error'
LENGTH_ERROR = 'length_error'
ENUM_ERROR = 'enum_error'

# PRIVATE VALUE THAT REPRESENTS MISSING KEY
__NOT_AVAILABLE__ = '__NOT_AVAILABLE__'


def err(error): return ({error.__name__: error.todict()})


class Error(object):
    __name__ = 'Error'

    def todict(self):
        r = vars(self)
        r.update({'type': self.__name__})
        return r


class _TypeError(Error):
    __name__ = TYPE_ERROR

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


class KeyMissingError(Error):
    __name__ = KEY_MISSING_ERROR


class NullError(Error):
    __name__ = NULL_ERROR


class LengthError(Error):
    __name__ = LENGTH_ERROR

    def __init__(
        self,
        actual_length=None,
        expected_min_length=None,
        expected_max_length=None
    ):
        self.actual_length = actual_length
        self.expected_min_length = expected_min_length
        self.expected_max_length = expected_max_length


class RangeError(Error):
    __name__ = RANGE_ERROR

    def __init__(
        self,
        actual_val,
        valid_range
    ):
        self.actual_val = actual_val
        self.valid_range = valid_range


class EnumError(Error):
    __name__ = ENUM_ERROR

    def __init__(self, actual, enums):
        self.actual = actual
        self.enums = enums
