from .utils import default_pre_clean, build_index
from .tokenizer import tokenize
from .parser import Parser
from .evaluator import Evaluator

class LexiQuery:
    """Query engine bound to a specific text (cleaned + indexed)."""
    def __init__(self, string: str, pre_clean = default_pre_clean):
        self.string_org = string
        self.string = pre_clean(string)
        self.index = build_index(self.string)

    def query(self, expression: str) -> bool:
        tokens = tokenize(expression)
        node = Parser(tokens).parse()
        return Evaluator(self.string, self.index).eval(node).matched

class LexiQueryExpression:
    """A validated expression that can be executed against texts."""
    def __init__(self, expression: str):
        if not test_lexi_grammar(expression):
            raise ValueError('Grammar Error')
        self.expression = expression

    def query(self, string: str) -> bool:
        return LexiQuery(string).query(self.expression)

    def query_list(self, string_list):
        return [s for s in string_list if self.query(s)]

def test_lexi_grammar(expr: str) -> bool:
    try:
        Parser(tokenize(expr)).parse()
        return True
    except Exception:
        return False
