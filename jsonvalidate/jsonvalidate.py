# -*- coding: utf-8 -*-

"""
    jsonvalidate.jsonvalidate
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Module that provides a helper classes for defining schema and validation for json
"""

TYPE_ERROR = 'type_error'
NULL_ERROR = 'null_error'
KEY_MISSING_ERROR = 'key_missing_error'
RANGE_ERROR = 'range_error'
LENGTH_ERROR = 'length_error'
ENUM_ERROR = 'enum_error'


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


class Contract(object):
    """Descriptor protocol"""
    # pylint: disable=
    def __init__(*args, **kwargs):
        pass

    def check(self, val):
        return False, None


class Type(Contract):
    """Abstract Base class for Type validation"""
    __name__ = 'Type'
    _type = None

    def __init__(self, *args, **kwargs):
        self.nullable = kwargs.get('nullable', False)
        super(Type, self).__init__(*args, **kwargs)

    def check(self, val):
        if not self.nullable and not isinstance(val, self._type):
            return True, _TypeError(self.__name__, type(val).__name__).todict()
        return super(Type, self).check(val)


class KeyMissingContract(Contract):

    def __init__(self, *args, **kwargs):
        # pop the optional key from the
        self.optional = None
        try:
            self.optional = kwargs.pop('optional')
        except KeyError:
            self.optional = False
        super(KeyMissingContract, self).__init__(*args, **kwargs)

    def check(self, val):
        _err = {}
        _err[KEY_MISSING_ERROR] = KeyMissingError().todict()
        if not self.optional and val == __NOT_AVAILABLE__:
            return True, _err
        return super(KeyMissingContract, self).check(val)


class NullContract(Contract):

    def __init__(self, *args, **kwargs):
        # pop the nullable key from the kwargs
        self.nullable = kwargs.get('nullable', False)

        super(NullContract, self).__init__(*args, **kwargs)

    def check(self, val):
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
        _err = {}
        if self.min_length and len(val) < self.min_length:
            return True, err(LengthError(
                actual_length=len(val),
                expected_min_length=self.min_length
            ))
        if self.max_length and len(val) > self.max_length:
            return True, err(LengthError(
                actual_length=len(val),
                expected_max_length=self.max_length
            ))
        return super(LengthContract, self).check(val)


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
    _type = str


class IntegerContract(Type):
    """Type Contract for Integer"""
    __name__ = 'Integer'
    _type = int


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
        r = {}
        if value is None:
            # that means we have a Null error
            r[NULL_ERROR] = NullError()

        if not isinstance(value, dict):
            r['type_error'] = _TypeError(
                self.__name__, type(value).__name__).todict()
            return True, r
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
        if type(object_shape) not in [List, Object, StringContract, IntegerContract, FloatContract, BooleanContract]:
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


def main():
    schema = Object({
        'name': String(max_length=3),
        'age': Integer(enums=[5, 6, 7]),
        'address': Object({
            'permanent': String(),
            'temporary': String(min_length=3, enums=['asss', 's'])
        }),
        'friends': List(Object({
            'name': String(),
            'nick_name': String()
        }))
    })

    list_schema = List(String(max_length=5))
    list_payload = ['asd', 2, 'asdasdasd']

    # print(list_schema.check(list_payload))
    payload = {
        'name': 'r',
        'age': 6,
        'address': {
            'permanent': 'sd',
            'temporary': 'asss'
        },
        'friends': [{'name': 'robus', 'nick_name': 'sd'}, 'sasdasdasd']

    }
    print(schema.check(payload))


if __name__ == '__main__':
    main()
