import orjson


def json_loads(text):
    if text:
        try:
            return orjson.loads(text)
        except orjson.JSONDecodeError:
            pass


def json_dumps(val, **kwargs):
    return orjson.dumps(val, **kwargs).decode('UTF-8')


if __name__ == '__main__':
    d = {'a': 1, 'b': 'test'}
    print(json_dumps(d, option=orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE))
