import pytest
from lexiquery import LexiQuery, LexiQueryExpression, GrammarError

def T(text, expr):
    return LexiQuery(text).query(expr)

def test_boolean_and_or_not_precedence():
    # NOT > AND > OR
    assert T("foo bar baz", "foo OR bar AND baz")  # bar AND baz -> True, OR foo also True
    assert not T("foo qux", "NOT foo AND qux")     # (NOT foo)=False AND qux=True -> False
    assert T("foo qux", "NOT (bar) AND qux")      # True AND True

def test_parentheses_grouping():
    assert T("foo baz", "(foo OR bar) AND baz")
    assert not T("bar qux", "(foo OR bar) AND baz")

def test_positional_near_bef_aft_defaults_and_dist():
    assert T("foo x bar", "foo NEAR/2 bar")
    assert not T("foo x y bar", "foo NEAR/1 bar")
    assert T("foo bar", "foo BEF/1 bar")
    assert T("bar foo", "foo AFT/1 bar")  # foo after bar within 1
    assert T("foo x y bar", "foo BEF/2-3 bar")
    assert T("foo a b c d bar", "foo BEF/* bar")
    assert T("bar a b c foo", "foo AFT/* bar")
    assert T("foo a b c bar", "foo NEAR/* bar")

def test_wildcards_suffix_operator_and_compact():
    assert T("foobar baz", "foo * NEAR/1 baz")   # explicit operator
    assert T("foobar baz", "foo* NEAR/1 baz")    # compact form

def test_match_ops_like_only_str_end():
    assert T("hello world", "LIKE hello world")
    assert not T("hello world world", "ONLY hello world foo")
    assert T("the quick brown", "STR the quick")
    assert T("over the lazy dog", "END lazy dog")
    assert T("hello   world", "STR hello world")
    assert T("over the   lazy    dog", "END lazy dog")

def test_expression_validation():
    with pytest.raises(ValueError):
        LexiQueryExpression("AND foo")  # invalid
    ok = LexiQueryExpression("foo AND bar")
    assert ok.query("foo bar")

def test_expression_validation_accepts_new_ops_and_uppercase_literals():
    expr_samples = [
        ("foo XOR bar", "foo baz"),
        ("LEN/3", "foo bar"),
        ("SIZE/20", "abc"),
        ("foo BEF/3 IN(bar baz)", "foo bar baz"),
        ("foo BEF/* INOF(bar baz)", "foo qux baz"),
        ("NASA AND rocket", "nasa rocket launch"),
    ]
    for expr, text in expr_samples:
        LexiQueryExpression(expr)
        assert LexiQuery(text).query(expr)

def test_grammar_errors_rigorous():
    # missing closing paren
    with pytest.raises(ValueError):
        LexiQueryExpression("(foo AND bar")
    # operators needing words
    with pytest.raises(ValueError):
        LexiQueryExpression("STR")
    with pytest.raises(ValueError):
        LexiQueryExpression("NEAR/2 foo")  # missing left word
    with pytest.raises(ValueError):
        LexiQueryExpression("IN(foo bar)")  # must follow positional op

def test_not_bind_tight():
    assert T("foo bar", "NOT foo OR bar") is True   # (NOT foo) OR bar -> True
    assert T("foo bar", "NOT (foo OR bar)") is False
    long_text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    expr = "(NOT (alpha AND omega)) AND LEN/20 AND (beta BEF/2 IN(gamma delta))"
    assert T(long_text, expr) is True

def test_complex_long_expression():
    corpus = [
        "intro", "alpha",
        "delta", "one", "epsilon",
        "delta", "two", "zeta",
        "eta", "foo", "bar", "theta",
        "iota", "bar", "baz",
        "kappa", "lambda", "mu",
        "omega", "sigma", "tau", "upsilon", "phi"
    ]
    text = " ".join(corpus)
    expr = (
        "LEN/20-40 AND NOT ((alpha AND beta) OR gamma) "
        "AND ((delta BEF/3 IN(epsilon zeta)) XOR (eta NEAR/2 theta)) "
        "AND (iota BEF/* INOF(kappa lambda mu))"
    )
    assert T(text, expr)

    # Make eta NEAR theta (distance 1) to flip the XOR clause and break the expression
    broken = corpus.copy()
    broken.remove("theta")
    insert_idx = broken.index("eta") + 1
    broken.insert(insert_idx, "theta")
    bad_text = " ".join(broken)
    assert not T(bad_text, expr)
