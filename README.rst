============
jsonvalidate
============


.. image:: https://img.shields.io/pypi/v/jsonvalidate.svg
        :target: https://pypi.python.org/pypi/jsonvalidate

.. image:: https://travis-ci.org/RobusGauli/jsonvalidate.svg?branch=master
        :target: https://travis-ci.org/RobusGauli/jsonvalidate

.. image:: https://readthedocs.org/projects/jsonvalidate/badge/?version=latest
        :target: https://jsonvalidate.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




JSON validation Schema


* Free software: MIT license
* Documentation: https://jsonvalidate.readthedocs.io.


Features
--------

```python

schema = Object({
        'name': String(),
        'age': Integer(enums=[5, 6, 7]),
        'address': Object({
            'permanent': String(),
            'temporary': String(min_length=3, enums=['asss', 's'])
        })
    })

    payload = {
        'name': 'robus',
        'age': 342,
        'address': {
            'permanent': 'sd',
            'temporary': 'asss'
        }

    }
    print(schema.check(payload))
   ```
