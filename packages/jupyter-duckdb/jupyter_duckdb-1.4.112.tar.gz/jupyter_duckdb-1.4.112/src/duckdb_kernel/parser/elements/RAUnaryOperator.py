from typing import Iterator

from .LogicElement import LogicElement
from .RAElement import RAElement
from .RAOperator import RAOperator
from ..tokenizer import Token


class RAUnaryOperator(RAOperator):
    @classmethod
    def parse_args(cls: type['RAUnaryOperator'], *tokens: Token, depth: int):
        from .. import LogicParser
        return LogicParser.parse_tokens(*tokens, depth=depth)

    def __init__(self, target: RAElement):
        self.target: RAElement = target

    @property
    def arg(self) -> LogicElement:
        raise NotImplementedError

    @property
    def conditions(self) -> str:
        return str(self.arg)

    def __str__(self, indent: int = 0) -> str:
        return f'{super().__str__(indent)} with arg=({self.arg})\n{self.target.__str__(indent + 1)}'

    @property
    def children(self) -> Iterator[RAElement]:
        yield self.target
