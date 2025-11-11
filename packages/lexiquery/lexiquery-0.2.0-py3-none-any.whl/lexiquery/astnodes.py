from dataclasses import dataclass
from typing import List

@dataclass
class Node: ...
@dataclass
class Word(Node):
    value: str
    wildcard: bool = False  # suffix wildcard

@dataclass
class MatchOp(Node):
    op: str
    words: List[Word]

@dataclass
class DistanceSpec:
    minimum: int
    maximum: int | None  # None => unlimited

@dataclass
class PosOp(Node):
    op: str   # NEAR/BEF/AFT
    distance: DistanceSpec
    left: Word
    right: Word

@dataclass
class PosSetOp(Node):
    op: str   # NEAR/BEF/AFT
    distance: DistanceSpec
    left: Word
    mode: str   # IN / INOF
    words: List[Word]

@dataclass
class LengthOp(Node):
    op: str   # LEN / SIZE
    minimum: int
    maximum: int | None

@dataclass
class Not(Node):
    expr: Node

@dataclass
class And(Node):
    left: Node
    right: Node

@dataclass
class Or(Node):
    left: Node
    right: Node

@dataclass
class Xor(Node):
    left: Node
    right: Node

@dataclass
class Group(Node):
    expr: Node
