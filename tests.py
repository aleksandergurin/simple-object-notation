
from son import loads, dumps


# Serialization tests
def test_null_serialize():
    assert dumps(None) == 'null'


def test_bool_serialize():
    assert dumps(True) == 'true'
    assert dumps(False) == 'false'


def test_number_serialize():
    assert dumps(123) == '123'
    assert dumps(-987) == '-987'
    assert dumps(0.1) == '0.1'
    assert dumps(0.00005) == '5e-05'
    assert dumps(-123e3) == '-123000.0'


def test_string_serialize():
    s = r'"\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b\t'        \
        r'\n\u000b\f\r\u000e\u000f\u0010\u0011\u0012\u0013\u0014'       \
        r'\u0015\u0016\u0017\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f"'

    assert dumps('\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009'
                 '\u000a\u000b\u000c\u000d\u000e\u000f\u0010\u0011\u0012\u0013\u0014'
                 '\u0015\u0016\u0017\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f') == s
    assert dumps('abcdefg') == '"abcdefg"'
    assert dumps('\u0391\u0392\u0393\u0394') == r'"\u0391\u0392\u0393\u0394"'
    assert dumps('\u0410\u0411\u0412\u0413') == r'"\u0410\u0411\u0412\u0413"'
    assert dumps('\u05d0\u05d1\u05d2\u05d3') == r'"\u05d0\u05d1\u05d2\u05d3"'


def test_array_serialize():
    assert dumps([1, 2, 3]) == '[1 2 3]'
    assert dumps([1, 2, 3], json_compatibility=True) == '[1, 2, 3]'
    assert dumps([[[[[[[[[["one", "two", "three"]]]]]]]]]]) == '[[[[[[[[[["one" "two" "three"]]]]]]]]]]'
    assert dumps([[1, 2], ["one", "two"]]) == '[[1 2] ["one" "two"]]'
    assert dumps([[1, 2], ["one", "two"]], json_compatibility=True) == '[[1, 2], ["one", "two"]]'


def test_object_serialize():
    assert dumps({"a": 1, "b": 2, "c": 3}, sorted_keys=True) == '{"a": 1 "b": 2 "c": 3}'
    assert dumps({"a": 1, "b": 2, "c": 3}, sorted_keys=True,
                 json_compatibility=True) == '{"a": 1, "b": 2, "c": 3}'
    assert dumps({"c": 12, "b": {"e": {}, "d": [{"f": 15}]}, "a": [[1, 2], [3, 4]]},
                 sorted_keys=True) == '{"a": [[1 2] [3 4]] "b": {"d": [{"f": 15}] "e": {}} "c": 12}'
    assert dumps({"c": 12, "b": {"e": {}, "d": [{"f": 15}]}, "a": [[1, 2], [3, 4]]}, sorted_keys=True,
                 json_compatibility=True) == '{"a": [[1, 2], [3, 4]], "b": {"d": [{"f": 15}], "e": {}}, "c": 12}'


# Deserialization tests
# TODO: add tests which should fail
def test_null_deserialize():
    assert loads('null') is None
    assert loads('   null   ') is None
    assert loads(' # comment\n null # comment') is None


def test_bool_deserialize():
    assert loads('true')
    assert loads('   true   ')
    assert loads(' # comment\n true # comment')
    assert not loads('false')
    assert not loads('   false   ')
    assert not loads(' # comment\n false # comment')


def test_int_number_deserialize():
    assert loads('5') == 5
    assert loads(' 5 ') == 5
    assert loads('-17') == -17
    assert loads(' -17 ') == -17
    assert loads(' # comment\n  -17  # comment') == -17


def test_float_number_deserialize():
    assert loads('5.0') == 5.0
    assert loads('  5.0  ') == 5.0
    assert loads('5e1') == 50.0
    assert loads('  -0.5e1  ') == -5.0
    assert loads(' # comment\n  -0.5e1  # comment') == -5.0


def test_string_deserialize():
    assert loads('"Testing"') == 'Testing'
    assert loads('   "Testing"   ') == 'Testing'
    assert loads(' # comment\n "Testing" # comment') == 'Testing'
    # the following assert test escape symbols "\" \\ \/ \b \f \n \r \t"
    assert loads(' # comment\n "\\" \\\\ \\/ \\b \\f \\n \\r \\t" # comment') == '" \\ / \b \f \n \r \t'


def test_string_with_unicode_symbols_deserialize():
    assert loads('"ΑΒΓΔ"') == 'ΑΒΓΔ'    # Greek
    assert loads('"АБВГ"') == 'АБВГ'    # Cyrillic
    assert loads('"אבגד"') == 'אבגד'    # Hebrew

    assert loads('"\\u0391\\u0392\\u0393\\u0394"') == '\u0391\u0392\u0393\u0394'    # Greek
    assert loads('"\\u0410\\u0411\\u0412\\u0413"') == '\u0410\u0411\u0412\u0413'    # Cyrillic
    # with lowercase hexadecimal symbols
    assert loads('"\\u05d0\\u05d1\\u05d2\\u05d3"') == '\u05d0\u05d1\u05d2\u05d3'    # Hebrew
    # with uppercase hexadecimal symbols
    assert loads('"\\u05D0\\u05D1\\u05D2\\u05D3"') == '\u05D0\u05D1\u05D2\u05D3'


def test_array_with_comma_separator_deserialize():
    assert loads(" [1,2,3] ") == [1, 2, 3]
    assert loads("[[[[[[[[[[1, 2, 3]]]]]]]]]]") == [[[[[[[[[[1, 2, 3]]]]]]]]]]
    assert loads('["string", 17, null, [true, false]]') == ["string", 17, None, [True, False]]
    assert loads(' # comment\n [ # comment\n "string" , 17 , # comment\n'
                 'null , \n[\n true,\nfalse\n]\n]') == ["string", 17, None, [True, False]]


def test_array_without_comma_separator_deserialize():
    assert loads(" [1 2 3] ") == [1, 2, 3]
    assert loads('["string" 17 null [true false]]') == ["string", 17, None, [True, False]]
    assert loads(' # comment\n [ # comment\n"string"\n17\n# comment\n'
                 'null\n[\ntrue\nfalse\n]\n ] ') == ["string", 17, None, [True, False]]


def test_object_with_comma_separator_deserialize():
    obj = loads(' # comment\n{\n  "one": 1, # comment\n  "two": { "inner": [1, 2, 3] } # comment\n} ')
    assert obj.get('one') == 1
    assert obj.get('two').get("inner") == [1, 2, 3]
    assert len(obj.keys()) == 2


def test_object_without_comma_separator_deserialize():
    obj = loads(' # comment\n{\n  "one": 1  # comment\n  "two": [1 2 3] "three": false  # comment\n} ')
    assert obj.get('one') == 1
    assert obj.get('two') == [1, 2, 3]
    assert not obj.get('three')
    assert len(obj.keys()) == 3
