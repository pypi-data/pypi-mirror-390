import pytest
from lexiquery import LexiQuery, LexiQueryExpression

def T(text, expr):
    return LexiQuery(text).query(expr)

def test_xor():
    assert T("foo baz", "foo XOR bar")
    assert not T("foo bar", "foo XOR bar")
    assert not T("qux", "foo XOR bar")

def test_positional_set_ops():
    assert T("foo a b", "foo BEF/2 IN(a b)")
    assert not T("foo a b", "foo BEF/1 IN(a b)")
    assert T("foo a c", "foo BEF/1 INOF(b a)")
    assert not T("foo c", "foo BEF/1 INOF(a b)")

def test_positional_ranges_and_star():
    assert T("foo x y z bar", "foo NEAR/3-4 bar")
    assert not T("foo x y z bar", "foo NEAR/1-2 bar")
    assert T("foo a b c d bar", "foo BEF/* bar")
    assert T("bar a b c foo", "foo AFT/* bar")

def test_len_and_size_ranges():
    assert T("one two three", "LEN/3")
    assert not T("one two three four", "LEN/3")
    assert T("alpha beta gamma delta epsilon", "LEN/3-6")
    assert T("abcde", "SIZE/5")
    assert not T("abcdefghijk", "SIZE/5")
    assert T("alpha beta gamma", "NOT LEN/2")
    assert T("abc", "NOT SIZE/2")

def test_length_ops_composable():
    expr = "LEN/5 AND foo BEF/3 bar"
    assert T("foo x bar", expr)
    assert not T("foo x y z bar", expr)

def test_invalid_length_specs():
    with pytest.raises(ValueError):
        LexiQueryExpression("LEN")
    with pytest.raises(ValueError):
        LexiQueryExpression("LEN/3-1")
    with pytest.raises(ValueError):
        LexiQueryExpression("SIZE")

def test_deeply_nested_boolean_expression():
    text = "alpha foo beta bar baz qux foo bar baz qux foo baz quux corge grault"
    expr = (
        "LEN/5-20 AND "
        "NOT ((foo BEF/1 bar) XOR (baz AFT/* qux)) AND "
        "((foo NEAR/1 bar) OR (baz BEF/2 qux)) AND "
        "(foo BEF/2 IN(bar baz)) AND "
        "NOT SIZE/5"
    )
    assert T(text, expr)
