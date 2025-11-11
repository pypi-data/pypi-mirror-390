from dataclasses import dataclass
from typing import Dict, List
from .astnodes import *
from .exceptions import GrammarError

@dataclass
class EvalResult:
    matched: bool
    positions: Dict[str, List[int]]  # token -> positions

def wildcard_positions(index: Dict[str, List[int]], prefix: str) -> List[int]:
    pos = []
    for tok, plist in index.items():
        if tok.startswith(prefix):
            pos.extend(plist)
    return sorted(pos)

def token_positions(index: Dict[str, List[int]], token: str, wildcard: bool) -> List[int]:
    if wildcard:
        return wildcard_positions(index, token)
    return index.get(token, [])

def distance(left: List[int], right: List[int]) -> List[int]:
    return [i - j for i in left for j in right]

def value_in_distance_spec(value: int, spec: DistanceSpec) -> bool:
    if value < spec.minimum:
        return False
    if spec.maximum is not None and value > spec.maximum:
        return False
    return True

def before_op(left: List[int], right: List[int], spec: DistanceSpec) -> bool:
    return any(d > 0 and value_in_distance_spec(d, spec) for d in distance(right, left))

def after_op(left: List[int], right: List[int], spec: DistanceSpec) -> bool:
    return any(d > 0 and value_in_distance_spec(d, spec) for d in distance(left, right))

def near_op(left: List[int], right: List[int], spec: DistanceSpec) -> bool:
    return any(value_in_distance_spec(abs(d), spec) for d in distance(left, right))

class Evaluator:
    def __init__(self, text: str, index: Dict[str, List[int]]):
        self.text = text
        self.index = index
        self.tokens = set(index.keys())
        self.token_sequence = self.text.split()

    def eval(self, node: Node) -> EvalResult:
        if isinstance(node, Group):
            return self.eval(node.expr)

        if isinstance(node, Word):
            pos = token_positions(self.index, node.value, node.wildcard)
            return EvalResult(bool(pos), {node.value: pos} if pos else {})

        if isinstance(node, MatchOp):
            words = [w.value for w in node.words]
            if node.op == 'ONLY':
                return EvalResult(set(words) == self.tokens, {})
            if node.op == 'LIKE':
                return EvalResult(all(w in self.tokens for w in words), {})
            if node.op == 'STR':
                starts = self.token_sequence[:len(words)]
                return EvalResult(starts == words, {})
            if node.op == 'END':
                if len(words) > len(self.token_sequence):
                    return EvalResult(False, {})
                tail = self.token_sequence[-len(words):]
                return EvalResult(tail == words, {})
            raise GrammarError(f"Unknown match op {node.op}")

        if isinstance(node, LengthOp):
            if node.op == 'LEN':
                metric = len(self.token_sequence)
            elif node.op == 'SIZE':
                metric = len(self.text.encode('utf-8'))
            else:
                raise GrammarError(f"Unknown length op {node.op}")
            matched = value_in_distance_spec(metric, DistanceSpec(node.minimum, node.maximum))
            return EvalResult(matched, {})

        if isinstance(node, PosOp):
            left = token_positions(self.index, node.left.value, node.left.wildcard)
            right = token_positions(self.index, node.right.value, node.right.wildcard)
            matched = self.eval_positional(node.op, node.distance, left, right)
            return EvalResult(matched, {})

        if isinstance(node, PosSetOp):
            left = token_positions(self.index, node.left.value, node.left.wildcard)
            if not left:
                return EvalResult(False, {})
            results = []
            for w in node.words:
                right = token_positions(self.index, w.value, w.wildcard)
                results.append(self.eval_positional(node.op, node.distance, left, right))
            matched = all(results) if node.mode == 'IN' else any(results)
            return EvalResult(matched, {})

        if isinstance(node, Not):
            r = self.eval(node.expr)
            return EvalResult(not r.matched, {})

        if isinstance(node, And):
            l = self.eval(node.left)
            r = self.eval(node.right)
            return EvalResult(l.matched and r.matched, {})

        if isinstance(node, Or):
            l = self.eval(node.left)
            r = self.eval(node.right)
            return EvalResult(l.matched or r.matched, {})

        if isinstance(node, Xor):
            l = self.eval(node.left)
            r = self.eval(node.right)
            return EvalResult((l.matched) ^ (r.matched), {})

        raise GrammarError("Unknown AST node type")

    def eval_positional(self, op: str, spec: DistanceSpec, left: List[int], right: List[int]) -> bool:
        if not left or not right:
            return False
        if op == 'NEAR':
            return near_op(left, right, spec)
        if op == 'BEF':
            return before_op(left, right, spec)
        if op == 'AFT':
            return after_op(left, right, spec)
        raise GrammarError(f"Unknown positional op {op}")
