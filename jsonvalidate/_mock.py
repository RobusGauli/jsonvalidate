from jsonvalidate import String, Object, Integer, List


def main():
    schema = Object({
        'name': String(optional=False),
        'age': Integer(optional=False),
        
    })

    payload = {
        "age": 3
    }
    print(schema.check(payload))


if __name__ == '__main__':
    main()
