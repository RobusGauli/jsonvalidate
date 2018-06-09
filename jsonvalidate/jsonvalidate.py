# -*- coding: utf-8 -*-

"""
    jsonvalidate.jsonvalidate
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Module that provides a helper classes for defining schema and validation for json
"""

class Error(object):
    
    def todict(self):
        return {'type': self.__class__.__name__, **vars(self)}

class TypeError(Error):
    
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


class Contract(object):
    """Descriptor protocol"""    
    @classmethod
    def check(cls, val):
        pass

class Type(Contract):
    """Abstract Base class for Type validation"""
    _type = None

    @classmethod
    def check(cls, val):
        if not isinstance(val, cls._type):
            error = TypeError(cls._type.__name__, type(val).__name__)
            return error.todict()


class String(Type):
    _type = str

class Integer(Type):
    _type = int

class Float(Type):
    _type = float

class Boolean(Type):
    _type = bool



def main():
    s = String.check(3)
    print(s)

if __name__ == '__main__':
    main()

