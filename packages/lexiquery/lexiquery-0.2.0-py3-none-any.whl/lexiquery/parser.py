from typing import List, Tuple
from .tokenizer import Token
from .astnodes import *
from .exceptions import GrammarError

class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0

    def peek(self) -> Token | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, kind: str | None = None) -> Token:
        t = self.peek()
        if t is None:
            raise GrammarError("Unexpected end of input")
        if kind and t.kind != kind:
            raise GrammarError(f"Expected {kind}, got {t.kind}")
        self.i += 1
        return t

    def parse(self) -> Node:
        node = self.parse_or()
        if self.peek() is not None:
            raise GrammarError("Trailing tokens after complete expression")
        return node

    def parse_or(self) -> Node:
        node = self.parse_and()
        while True:
            t = self.peek()
            if t and t.kind == 'OP' and t.value in ('OR', 'XOR'):
                op = self.eat('OP').value
                right = self.parse_and()
                node = Or(node, right) if op == 'OR' else Xor(node, right)
            else:
                break
        return node

    def parse_and(self) -> Node:
        node = self.parse_not()
        while True:
            t = self.peek()
            if t and t.kind == 'OP' and t.value == 'AND':
                self.eat('OP')
                right = self.parse_not()
                node = And(node, right)
            else:
                break
        return node

    def parse_not(self) -> Node:
        t = self.peek()
        if t and t.kind == 'OP' and t.value == 'NOT':
            self.eat('OP')
            expr = self.parse_not()
            return Not(expr)
        return self.parse_atom()

    def parse_atom(self) -> Node:
        t = self.peek()
        if t is None:
            raise GrammarError("Empty expression")

        if t.kind == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_or()
            if not (self.peek() and self.peek().kind == 'RPAREN'):
                raise GrammarError("BO5: Missing closing parenthesis")
            self.eat('RPAREN')
            return Group(node)

        if t.kind == 'OP' and t.value in ('STR', 'END', 'LIKE', 'ONLY'):
            return self.parse_match_expression()

        if t.kind == 'OP' and t.value.startswith(('LEN', 'SIZE')):
            return self.parse_length_expression()

        left_word = self.parse_word_with_optional_star()
        t = self.peek()
        if t and t.kind == 'OP' and t.value.startswith(('NEAR', 'BEF', 'AFT')):
            op_value = self.eat('OP').value
            op_name, raw_spec = self.split_operator(op_value)
            distance = self.parse_distance_spec(op_name, raw_spec)
            next_tok = self.peek()
            if next_tok and next_tok.kind == 'OP' and next_tok.value in ('IN', 'INOF'):
                mode = self.eat('OP').value
                words = self.parse_parenthesized_word_list(mode)
                return PosSetOp(op_name, distance, left_word, mode, words)
            right_word = self.parse_word_with_optional_star()
            return PosOp(op_name, distance, left_word, right_word)

        return left_word

    def parse_match_expression(self) -> MatchOp:
        op = self.eat('OP').value
        words: List[Word] = []
        if not (self.peek() and self.peek().kind == 'WORD'):
            raise GrammarError(f"{op} must be followed by at least one word")
        while self.peek() and self.peek().kind == 'WORD':
            w = self.eat('WORD').value
            words.append(Word(w))
        return MatchOp(op, words)

    def parse_length_expression(self) -> LengthOp:
        token_value = self.eat('OP').value
        if '/' not in token_value:
            raise GrammarError("LO1: Length operators require bounds such as LEN/3 or LEN/2-5")
        op_name, raw_spec = token_value.split('/', 1)
        minimum, maximum = self.parse_numeric_range(raw_spec, 0)
        return LengthOp(op_name, minimum, maximum)

    def parse_numeric_range(self, fragment: str, default_minimum: int) -> Tuple[int, int]:
        if '-' in fragment:
            lo_str, hi_str = fragment.split('-', 1)
            try:
                lo = int(lo_str)
                hi = int(hi_str)
            except ValueError:
                raise GrammarError("LO1: Length range must use integers")
            if lo < default_minimum:
                raise GrammarError("LO1: Lower bound must be >= minimum allowed value")
            if hi < lo:
                raise GrammarError("LO1: Lower bound cannot exceed upper bound")
            return lo, hi
        try:
            hi = int(fragment)
        except ValueError:
            raise GrammarError("LO1: Length upper bound must be an integer")
        if hi < default_minimum:
            raise GrammarError("LO1: Upper bound must be >= minimum allowed value")
        return default_minimum, hi

    def split_operator(self, token_value: str) -> Tuple[str, str | None]:
        if '/' in token_value:
            return token_value.split('/', 1)
        return token_value, None

    def parse_distance_spec(self, op_name: str, fragment: str | None) -> DistanceSpec:
        if fragment is None:
            return DistanceSpec(0, 1) if op_name == 'NEAR' else DistanceSpec(1, 1)
        if fragment == '*':
            return DistanceSpec(0 if op_name == 'NEAR' else 1, None)
        if '-' in fragment:
            lo_str, hi_str = fragment.split('-', 1)
            try:
                lo = int(lo_str)
                hi = int(hi_str)
            except ValueError:
                raise GrammarError("PP2: Distance range must use integers")
            min_allowed = 0 if op_name == 'NEAR' else 1
            if lo < min_allowed:
                raise GrammarError("PP2: Distance range lower bound too small")
            if hi < lo:
                raise GrammarError("PP2: Distance range lower bound exceeds upper bound")
            return DistanceSpec(lo, hi)
        try:
            maximum = int(fragment)
        except ValueError:
            raise GrammarError("PP2: Distance must be integer, range, or *")
        min_allowed = 0 if op_name == 'NEAR' else 1
        if maximum < min_allowed:
            raise GrammarError("PP2: Distance must be >= minimum allowed value")
        return DistanceSpec(min_allowed, maximum)

    def parse_parenthesized_word_list(self, mode: str) -> List[Word]:
        if not (self.peek() and self.peek().kind == 'LPAREN'):
            raise GrammarError(f"{mode} must be followed by a parenthesized word list")
        self.eat('LPAREN')
        words: List[Word] = []
        if not (self.peek() and self.peek().kind == 'WORD'):
            raise GrammarError(f"{mode}(...) requires at least one word")
        while self.peek() and self.peek().kind == 'WORD':
            w = self.eat('WORD').value
            words.append(Word(w))
        if not (self.peek() and self.peek().kind == 'RPAREN'):
            raise GrammarError(f"Missing closing parenthesis in {mode}(...)")
        self.eat('RPAREN')
        return words

    def parse_word_with_optional_star(self) -> Word:
        t = self.peek()
        if t and t.kind == 'OP' and t.value in ('IN', 'INOF'):
            raise GrammarError("SO1: IN and INOF must follow a positional operator")
        if not (t and t.kind == 'WORD'):
            raise GrammarError("Expected word")
        w = self.eat('WORD').value
        wildcard = False
        if self.peek() and self.peek().kind == 'STAR':
            self.eat('STAR')
            wildcard = True
        return Word(w, wildcard)
