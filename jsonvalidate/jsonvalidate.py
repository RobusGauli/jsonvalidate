# -*- coding: utf-8 -*-

"""
    jsonvalidate.jsonvalidate
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Module that provides a helper classes for defining schema and validation for json
"""
import functools
from collections import defaultdict


TYPE_ERROR = 'type_error'
NULL_ERROR = 'null_error'
KEY_MISSING_ERROR = 'key_missing_error'
RANGE_ERROR = 'range_error'
LENGTH_ERROR = 'length_error'

__NOT_AVAILABLE__ = '__NOT_AVAILABLE__'

class Error(object):
    __name__ = 'Error'

    def todict(self):
        r = vars(self)
        r.update({'type': self.__name__})
        return r

class _TypeError(Error):
    __name__ = 'TypeError'

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual

class KeyMissingError(Error):
    __name__ = 'KeyMissingError'

class NullError(Error):
    __name__ = 'NullError'

class LengthError(Error):
    __name__ = 'LengthError'

    def __init__(
        self,
        actual_length = None,
        expected_min_length = None,
        expected_max_length = None
    ):
        self.actual_length = actual_length
        self.expected_min_length = expected_min_length
        self.expected_max_length = expected_max_length
    

class Contract(object):
    """Descriptor protocol"""    
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
        return super().check(val)
        
        
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
        self.min_length = None
        self.max_length = None

        try:
            self.min_length = kwargs.pop('min_length')
            if not isinstance(self.min_length, int):
                raise TypeError('min_length must be of type int.')
            self.max_length = kwargs.pop('max_length')
            if not isinstance(self.max_length, int):
                raise TypeError('max_length must be of type int.')
        except:
            pass
        
        super(LengthContract, self).__init__(*args, **kwargs)
    
    def check(self, val):
        _err = {}
        if self.min_length and len(val) < self.min_length:
            _err[LENGTH_ERROR] = LengthError(actual_length=len(val), expected_min_length=self.min_length)
            return True, _err
        if self.max_length and len(val) > self.max_length:
            _err[LENGTH_ERROR] = LengthError(
                actual_length=len(val),
                expected_max_length=self.max_length
            )
            return True, _err
        return super(LengthContract, self).check(val)
class _String(Type):
    """Type Contract for String"""
    __name__ = 'String'
    _type = str

class _Integer(Type):
    """Type Contract for Integer"""
    __name__ = 'Integer'
    _type = int

class _Float(Type):
    """Type Contract for Float"""
    __name__ = 'Float'
    _type = float

class _Boolean(Type):
    __name__ = 'Boolean'
    """Type Contract for Boolean"""
    _type = bool

    

class String(KeyMissingContract, NullContract, _String):
    pass

class Integer(KeyMissingContract, NullContract, _Integer):
    pass

class Float(KeyMissingContract, NullContract, _Float):
    pass

class Boolean(KeyMissingContract, NullContract, _Boolean):
    pass

        
class Object(Contract):
    __name__ = 'Object'

    def __init__(self, object_shape):
        if not isinstance(object_shape, dict):
            raise TypeError('Requires argument of type dict as a validation Schema.')
        self.object_shape = object_shape

    def check(self, value):
        # make sure that val of type is of dict
        r = {}
        if value is None:
            # that means we have a Null error
            r[NULL_ERROR] = NullError()
        if not isinstance(value, dict):
            r['type_error'] = _TypeError(self.__name__, type(value).__name__).todict()
            return True, r
        error = False
        result = {}
        for key, contract in self.object_shape.items():
            # grab the value or None
            _val = value.get(key, __NOT_AVAILABLE__)
            print(contract.__class__.__name__)
            _error, _result = contract.check(_val)
            if _error:
                error = True
            result[key] = _result
        return error, result
    
            

def main():
    schema = Object({
        'name': String(),
        'age': Integer(),
        'address': Object({
            'permanent': String(),
            'temporary': String(optional=True, nullable=False)
        })
    })

    payload = {
        'name': 'robus',
        'age': 34,
        'address': {
            'permanent': 'sd'
        }

    }
    print(schema.check(payload))

if __name__ == '__main__':
    main()

