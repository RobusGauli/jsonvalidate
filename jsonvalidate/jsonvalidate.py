# -*- coding: utf-8 -*-

"""
    jsonvalidate.jsonvalidate
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Module that provides a helper classes for defining schema and validation for json
"""

import re
import six

TYPE_ERROR = 'type_error'
NULL_ERROR = 'null_error'
KEY_MISSING_ERROR = 'key_missing_error'
RANGE_ERROR = 'range_error'
LENGTH_ERROR = 'length_error'
ENUM_ERROR = 'enum_error'
REGEX_ERROR = 'regex_error'


__NOT_AVAILABLE__ = '__NOT_AVAILABLE__'

# pylint: disable=too-few-public-methods


def err(error):
    """
        Utility function for returning serializable json payload.
    """
    return {error.__name__: error.todict()}


class Error(object):
    """Base class that is subclassed by Concrete error types."""
    __name__ = 'Error'

    def todict(self): # pylint disable=to-few-public-methods
        """
            Converts python object to serializable dictionary.
        """
        r = vars(self)
        r.update({'type': self.__name__})
        return r

    def __repr__(self):
        return self.__name__


class _TypeError(Error):
    """A class that represents type mismatch"""
    __name__ = TYPE_ERROR

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


class KeyMissingError(Error):
    """A class that represents key mismatch error"""
    __name__ = KEY_MISSING_ERROR


class NullError(Error):
    """A class that represents null error"""
    __name__ = NULL_ERROR


class RegExError(Error):
    """A class that represents regex error"""
    __name__ = REGEX_ERROR


class LengthError(Error):
    """A class that represents length invalidation error"""
    __name__ = LENGTH_ERROR

    def __init__(self, actual_length=None, expected_min_length=None, expected_max_length=None):
        """
        :param actual_length
        :param expected_min_length
        :param expected_max_lengt
        """
        self.actual_length = actual_length
        self.expected_min_length = expected_min_length
        self.expected_max_length = expected_max_length

class RangeError(Error):
    """A subclass of error for range validation"""
    __name__ = RANGE_ERROR

    def __init__(self, actual_val, valid_range):
        """
        :param actual_val
        :param valid_range
        """
        self.actual_val = actual_val
        self.valid_range = valid_range


class EnumError(Error):
    """A class that represents enum invalidation error"""
    __name__ = ENUM_ERROR

    def __init__(self, actual, enums):
        self.actual = actual
        self.enums = enums


# pylint: disable=no-self-use
class Contract(object):  # pylint: disable=too-few-public-methods
    """Abstract Base class for both primitives types"""

    # pylint: disable=too-few-public-methods

    def __init__(self, *args, **kwargs):
        pass

    def check(self, *args):
        """last method in MRO chain that will eventually return false as an error"""
        return False, None


class Type(Contract):
    """Abstract Base class for Type validation"""
    __name__ = 'Type'
    _type = None

    def __init__(self, *args, **kwargs):
        self.optional = kwargs.get('optional', False)
        self.nullable = kwargs.get('nullable', False)
        super(Type, self).__init__(*args, **kwargs)

    def check(self, val):
        """
            Checks for type mismatch.
        """
        if not self.optional and (not self.nullable and not isinstance(val, self._type)):
            return True, _TypeError(self.__name__, type(val).__name__).todict()
        return super(Type, self).check(val)


class KeyMissingContract(Contract):

    def __init__(self, *args, **kwargs):
        self.optional = kwargs.get('optional', False)
        super(KeyMissingContract, self).__init__(*args, **kwargs)

    def check(self, val):
        """
            Checks for key mismatch
        """
        _err = {}
        _err[KEY_MISSING_ERROR] = KeyMissingError().todict()
        if not self.optional and val == __NOT_AVAILABLE__:
            return True, _err
        return super(KeyMissingContract, self).check(val)


class NullContract(Contract):
    """A Null Contract class that implements check method for nullable value"""
    def __init__(self, *args, **kwargs):
        # pop the nullable key from the kwargs
        self.nullable = kwargs.get('nullable', False)

        super(NullContract, self).__init__(*args, **kwargs)

    def check(self, val):
        """Checks if the value is null and delegate the method call to next method in MRO"""
        _err = {}
        if not self.nullable and val is None:
            _err[NULL_ERROR] = NullError().todict()
            return True, _err
        return super(NullContract, self).check(val)


class LengthContract(Contract):

    def __init__(self, *args, **kwargs):

        self.min_length = kwargs.get('min_length')
        if self.min_length and not isinstance(self.min_length, int):
            raise TypeError('min_length must be of type int.')
        self.max_length = kwargs.get('max_length')
        if self.max_length and not isinstance(self.max_length, int):
            raise TypeError('max_length must be of type int.')

        super(LengthContract, self).__init__(*args, **kwargs)

    def check(self, val):
        value_length = 0 if val == __NOT_AVAILABLE__ else len(val)

        if self.min_length and value_length < self.min_length:
            return True, err(LengthError(
                actual_length=value_length,
                expected_min_length=self.min_length
            ))
        if self.max_length and value_length > self.max_length:
            return True, err(LengthError(
                actual_length=value_length,
                expected_max_length=self.max_length
            ))
        return super(LengthContract, self).check(val)


class RegExContract(Contract):

    def __init__(self, *args, **kwargs):
        # pop the regex key from the kwargs
        self.regex = kwargs.get('regex', False)

        super(RegExContract, self).__init__(*args, **kwargs)

    def check(self, val):
        """Checks if the value match regex and delegate the method call to next method in MRO"""
        if self.regex:
            try:
                regex = r"{}".format(self.regex)
                if re.compile(regex) and not re.match(regex, val):
                    return True, err(RegExError())
            except re.error as error:
                raise ValueError('invalid regular expression')
        return super(RegExContract, self).check(val)


class RangeContract(Contract):
    """Applicable to Integer"""

    def __init__(self, *args, **kwargs):
        self.range = kwargs.get('range', None)
        if self.range:
            if not isinstance(self.range, list):
                raise TypeError('range argument must be of type list.')

            if not all(type(val) in [int, float] for val in self.range):
                raise TypeError('Range argument must be of type int or float')

            if len(self.range) != 2 or self.range[0] >= self.range[1]:
                raise ValueError('Invalid range argument.')

        super(RangeContract, self).__init__(*args, **kwargs)

    def check(self, val):
        if self.range and (val < self.range[0] or val > self.range[1]):
            return True, err(RangeError(val, self.range))
        return super(RangeContract, self).check(val)


class EnumContract(Contract):

    def __init__(self, *args, **kwargs):
        self.enums = kwargs.get('enums', None)

        if self.enums:
            if not isinstance(self.enums, list):
                raise TypeError('enums must be of type list')
        super(EnumContract, self).__init__(*args, **kwargs)

    def check(self, val):
        if self.enums and val not in self.enums:
            return True, err(EnumError(val, self.enums))
        return super(EnumContract, self).check(val)


class StringContract(Type):
    """Type Contract for String"""
    __name__ = 'String'
    _type = six.string_types


class IntegerContract(Type):
    """Type Contract for Integer"""
    __name__ = 'Integer'
    _type = six.integer_types


class FloatContract(Type):
    """Type Contract for Float"""
    __name__ = 'Float'
    _type = float


class BooleanContract(Type):
    __name__ = 'Boolean'
    """Type Contract for Boolean"""
    _type = bool


class Object(Contract):
    __name__ = 'Object'

    def __init__(self, object_shape):
        if not isinstance(object_shape, dict):
            raise TypeError(
                'Requires argument of type dict as a validation Schema.')
        self.object_shape = object_shape

    def check(self, value):
        # make sure that val of type is of dict
        if value is None:
            # that means we have a Null error
            return True, err(NullError())

        if not isinstance(value, dict):
            return True, err(_TypeError(
                self.__name__,
                type(value).__name__
            ))
        error = False
        result = {}
        for key, contract in self.object_shape.items():
            # grab the value or None
            _val = value.get(key, __NOT_AVAILABLE__)
            _error, _result = contract.check(_val)
            if _error:
                error = True
            result[key] = _result
        return error, result


class List(Contract):
    __name__ = 'List'

    def __init__(self, object_shape):
        if not isinstance(object_shape, Contract):
            raise TypeError('Must be of valid type of list.')
        self.object_shape = object_shape

    def check(self, value):
        if value is None:
            return True, err(NullError())

        if not isinstance(value, list):
            return True, err(_TypeError(
                self.__name__,
                type(value).__name__
            ))
        # if this is the list then we need to traverse the list
        error = False
        result = {}
        for index, val in enumerate(value):
            _error, _result = self.object_shape.check(val)
            if _error:
                error = True
            result[index] = _result
        return error, result
