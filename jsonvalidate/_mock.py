from jsonvalidate import String, Object, Integer, List


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
