# Public Domain.
# NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
# Original JSON data format was specified by Douglas Crockford.
# Links:
# https://github.com/aleksandergurin/simple-object-notation
# http://json.org
# https://github.com/douglascrockford/JSON-js
# https://tools.ietf.org/html/rfc7159


"""SON (Simple Object Notation) data interchange format.

Simple data format similar to JSON, but with some minor changes:
    - comments starts with # sign and ends with newline (\n)
    - comma after a key-value pair is optional
    - comma after an array element is optional

JSON is compatible with SON in a sense that
JSON data is also SON data, but not vise versa.

SON data example:

    {
        # Personal information

        "name": "Alexander Grothendieck"
        "fields": "mathematics"
        "main_topics": ["Etale cohomology"  "Motives"  "Topos theory"  "Schemes"]
    }

"""

import re
import io
import math


class Consts:
    number_re = re.compile(r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?')

    escape_deserialize = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t'
    }

    escape_serialize = {
        '"': '\\"',
        '\\': '\\\\',
        '/': '\\/',
        '\b': '\\b',
        '\f': '\\f',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t'
    }


def dumps(obj, sorted_keys=False, json_compatibility=False):
    """Serialize an input Python object into SON data.
    Note: object could not have a circular references
    (in case when circular reference found ValueError
    will be raised).

    :param obj: an input Python object
    :return: string containing serialized SON data
    """

    circular_refs = {}
    buf = io.StringIO()

    def string_val(s):
        buf.write('"')
        for c in s:
            if Consts.escape_serialize.get(c):
                buf.write(Consts.escape_serialize.get(c))
            elif 0x1f < ord(c) < 0x7f:
                buf.write(c)
            else:
                buf.write('\\u{:04x}'.format(ord(c)))
        buf.write('"')

    def array_val(a):
        buf.write('[')
        if len(a) != 0:
            value(a[0])
            for i in range(1, len(a)):
                if json_compatibility:
                    buf.write(',')
                buf.write(' ')
                value(a[i])
        buf.write(']')

    def object_val(o):
        buf.write('{')

        if len(o) != 0:
            if sorted_keys:
                keys = sorted(o)
            else:
                keys = list(o.keys())
            string_val(str(keys[0]))
            buf.write(': ')
            value(o.get(keys[0]))
            for i in range(1, len(o)):
                if json_compatibility:
                    buf.write(',')
                buf.write(' ')
                string_val(str(keys[i]))
                buf.write(': ')
                value(o.get(keys[i]))
        buf.write('}')

    def value(x):
        if isinstance(x, bool):
            if x:
                buf.write('true')
            else:
                buf.write('false')
        elif x is None:
            buf.write('null')
        elif isinstance(x, int):
            # We have to create an int instance because
            # subclass of int could override __repr__ method
            buf.write(repr(int(x)))
        elif isinstance(x, float):
            if math.isinf(x) or math.isnan(x):
                raise ValueError("Out of range float value {}".format(x))
            # We have to create an float instance because
            # subclass of float could override __repr__ method
            buf.write(repr(float(x)))
        elif isinstance(x, str):
            string_val(x)
        elif isinstance(x, dict):
            if id(x) in circular_refs:
                raise ValueError("Circular reference detected")
            else:
                circular_refs[id(x)] = x
                object_val(x)
        elif isinstance(x, list) or isinstance(x, tuple):
            if id(x) in circular_refs:
                raise ValueError("Circular reference detected")
            else:
                circular_refs[id(x)] = x
                array_val(x)
        else:
            raise TypeError("{} is not serializable".format(str(x)))

    value(obj)

    return buf.getvalue()


def loads(input_str):
    """Deserialize input SON data to a Python object.

    :param input_str: string containing SON data
    :return: python object (dict, list, str, bool or None)
    """
    if not isinstance(input_str, str):
        raise TypeError("Input object must be a string")

    it = enumerate(input_str)
    ch, at, line, column = " ", 0, 0, 0

    def next_ch():
        nonlocal ch, at, line, column
        try:
            at, ch = next(it)
            if ch == '\n':
                line += 1
                column = 0
            else:
                column += 1
        except StopIteration:
            ch = None

    def skip_off(n):
        for i in range(n):
            next_ch()

    def error(message):
        # we use 0-based indexes, so we need to add 1 to 'line' and 'at'
        raise ValueError("{}: line {}, column {}".format(message, line + 1, column + 1))

    def literal_val():
        if input_str[at:at + 4] == "null":
            skip_off(4)
            return None
        elif input_str[at:at + 4] == "true":
            skip_off(4)
            return True
        elif input_str[at:at + 5] == "false":
            skip_off(5)
            return False
        else:
            error("Unexpected value")

    def number_val():
        m = Consts.number_re.match(input_str, at)
        if m is not None:
            integer, fraction, exp = m.groups()
            if fraction or exp:
                s = integer + (fraction or '') + (exp or '')
                skip_off(len(s))
                res = float(s)
            else:
                s = integer
                skip_off(len(s))
                res = int(s)
            return res
        else:
            error("Bad number")

    def string_val():
        if ch != '"':
            error("Expecting '\"'")
        next_ch()

        res = io.StringIO()
        while ch:
            if ch == '\"':
                next_ch()
                return res.getvalue()
            if ch == '\\':
                next_ch()
                if not ch:
                    break
                esc_ch = Consts.escape_deserialize.get(ch)
                if esc_ch:
                    res.write(esc_ch)
                    next_ch()
                elif ch == 'u':
                    next_ch()
                    if not ch:
                        break
                    try:
                        xxxx = input_str[at:at + 4]
                        if len(xxxx) != 4:
                            error("Invalid \\uXXXX escape")
                        skip_off(4)
                        res.write(chr(int(xxxx, 16)))
                    except ValueError:
                        error("Invalid \\uXXXX escape")
                else:
                    error("Invalid escape")
            else:
                res.write(ch)
                next_ch()
        error("Bad string")

    def array_val():
        if ch != '[':
            error("Expecting '['")
        next_ch()
        skip_spaces_and_comments()

        res = []

        if ch == ']':
            next_ch()
            return res

        while ch:
            # skip_spaces_and_comments() will be called
            # inside value() before and after actual token
            res.append(value())
            if ch == ']':
                next_ch()
                return res
            if ch == ',':
                next_ch()
                # skip_spaces_and_comments() will be called
                # inside value() during the next loop iteration
        error("Bad array")

    def object_val():
        if ch != '{':
            error("Expecting '{'")
        next_ch()
        skip_spaces_and_comments()

        res = {}

        if ch == '}':
            next_ch()
            return res

        while ch:
            if ch != '"':
                error("Expecting property name enclosed in '\"'")
            key = string_val()
            skip_spaces_and_comments()
            if ch != ':':
                error("Expecting ':' delimiter")
            # skip ':'
            next_ch()
            # skip_spaces_and_comments() will be called
            # inside value() before and after actual token
            res[key] = value()
            if ch == '}':
                next_ch()
                return res
            if ch == ',':
                next_ch()
                skip_spaces_and_comments()
        error("Bad object")

    def value():
        skip_spaces_and_comments()

        if ch == '{':
            res = object_val()
        elif ch == '[':
            res = array_val()
        elif ch == '"':
            res = string_val()
        elif ('0' <= ch <= '9') or ch == '-':
            res = number_val()
        else:
            res = literal_val()

        skip_spaces_and_comments()

        return res

    def skip_spaces_and_comments():
        while ch:
            if ch.isspace():
                next_ch()
            elif ch == '#':
                while ch and ch != '\n':
                    next_ch()
            else:
                break

    result = value()

    if ch:
        error("Extra data")

    return result


encode = dumps
decode = loads
