# -*- coding: utf-8 -*-

"""
    jsonvalidate.jsonvalidate
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Module that provides a helper classes for defining schema and validation for json
"""

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

class MissError(Error):
    __name__ = 'MissingError'


class Contract(object):
    """Descriptor protocol"""    
    @classmethod
    def check(cls, val):
        pass

class Type(object):
    """Abstract Base class for Type validation"""
    __name__ = 'Type'
    _type = None

    def __init__(self, optional=False):
        self.optional = optional
    
    def check(self, val):
        if not self.optional and val is None:
            return True, MissError().todict()

        if not self.optional and not isinstance(val, self._type):
            return True, _TypeError(self.__name__, type(val).__name__).todict()
        return False, None
        
        

class String(Type):
    """Type Contract for String"""
    __name__ = 'String'
    _type = str

class Integer(Type):
    """Type Contract for Integer"""
    __name__ = 'Integer'
    _type = int

class Float(Type):
    """Type Contract for Float"""
    __name__ = 'Float'
    _type = float

class Boolean(Type):
    __name__ = 'Boolean'
    """Type Contract for Boolean"""
    _type = bool


class Object(Contract):
    __name__ = 'Object'

    def __init__(self, object_shape):
        if not isinstance(object_shape, dict):
            raise TypeError('Requires argument of type dict as a validation Schema.')
        self.object_shape = object_shape
    
    def check(self, value):
        # make sure that val of type is of dict
        if not isinstance(value, dict):
            return True, _TypeError(self.__name__, type(value).__name__).todict()
        error = False
        result = {}
        for key, contract in self.object_shape.items():
            # grab the value or None
            _val = value.get(key)
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
            'temporary': String(optional=False)
        })
    })

    payload = {
        'name': 'robus',
        'age': 34,
        'address': 3

    }
    print(schema.check(payload))

if __name__ == '__main__':
    main()

