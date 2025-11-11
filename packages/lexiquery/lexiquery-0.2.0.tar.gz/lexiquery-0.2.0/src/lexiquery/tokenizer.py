import re
from dataclasses import dataclass
from typing import List

OP_RE = re.compile(
    r'^(AND|OR|XOR|NOT|IN|INOF|'
    r'NEAR(?:/(?:\*|\d+(?:-\d+)?))?|'
    r'BEF(?:/(?:\*|\d+(?:-\d+)?))?|'
    r'AFT(?:/(?:\*|\d+(?:-\d+)?))?|'
    r'LEN(?:/\d+(?:-\d+)?)?|'
    r'SIZE(?:/\d+(?:-\d+)?)?|'
    r'STR|END|LIKE|ONLY|\(|\)|\*)$',
    re.IGNORECASE,
)

@dataclass
class Token:
    kind: str   # WORD, OP, LPAREN, RPAREN, STAR
    value: str

def tokenize(expr: str) -> List[Token]:
    # normalize compact wildcards: foo* -> foo *
    expr = re.sub(r'(\w+)\*', r'\1 *', expr)
    expr = re.sub(r'([()])', r' \1 ', expr)
    raw = expr.strip().split()
    tokens: List[Token] = []
    for r in raw:
        if r == '(':
            tokens.append(Token('LPAREN', r))
        elif r == ')':
            tokens.append(Token('RPAREN', r))
        elif OP_RE.match(r):
            val = r.upper()
            if val == '*':
                tokens.append(Token('STAR', '*'))
            elif val == '(':
                tokens.append(Token('LPAREN', val))
            elif val == ')':
                tokens.append(Token('RPAREN', val))
            else:
                tokens.append(Token('OP', val))
        else:
            tokens.append(Token('WORD', r.lower()))
    return tokens
