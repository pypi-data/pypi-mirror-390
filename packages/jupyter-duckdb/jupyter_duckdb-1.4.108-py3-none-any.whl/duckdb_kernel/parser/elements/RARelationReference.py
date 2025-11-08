import re

from . import RAUnaryOperator
from .LogicElement import LogicElement
from ..ParserError import RAParserError
from ..tokenizer import Token


class RARelationReference(LogicElement):
    @staticmethod
    def parse_tokens(operator: type[RAUnaryOperator], *tokens: Token, depth: int = 0) -> 'RARelationReference':
        try:
            # If we get one single token, it should be like
            # R -> "R"
            # [ R ] -> "R"
            # [ R(A, B, C) ] -> "R(A, B, C)"
            # (A, B, C) -> "(A, B, C")
            # [ (A, B, C) ] -> "(A, B, C)"
            if len(tokens) == 1:
                return RARelationReference._parse_one_token(*tokens)

            # If we get two tokens, it should be like
            # R(A, B, C) -> "R", "A, B, C"
            # R A -> "R", "A"
            # (The latter equals R(A), but we should think about rejecting this type.)
            elif len(tokens) == 2:
                return RARelationReference._parse_two_tokens(*tokens)

            # Otherwise, the input is malformed.
            else:
                raise AssertionError()

        except AssertionError:
            raise RAParserError(f'malformed input for operator {operator.symbols()[0]} {tokens=}', depth=depth)

    @staticmethod
    def _parse_one_token(token: Token) -> 'RARelationReference':
        match = re.fullmatch(r'^\s*([A-Za-z0-9]+)?\s*(\(?((\s*[A-Za-z0-9]+\s*,\s*)*(\s*[A-Za-z0-9]+\s*,?\s*))\)?)?\s*$', token)
        if match is None:
            raise AssertionError()

        if match.group(1) is not None:
            relation = match.group(1).strip()
        else:
            relation = None

        if match.group(3) is not None:
            attributes = [b for b in (a.strip() for a in match.group(3).split(',')) if b != '']
        else:
            attributes = None

        if relation is None and attributes is None:
            raise AssertionError()

        return RARelationReference(relation, attributes)

    @staticmethod
    def _parse_two_tokens(token1: Token, token2: Token) -> 'RARelationReference':
        # We expect the first token to be a relation name and the second one
        # to be a list of column names separated by commas.
        relation = token1.strip()
        attributes = [b for b in (a.strip() for a in token2.split(',')) if b != '']

        return RARelationReference(relation, attributes)

    def __init__(self, relation: str | None, attributes: list[str] | None):
        # check duplicated attributes
        if attributes is not None:
            for i in range(len(attributes)):
                for k in range(i + 1, len(attributes)):
                    if attributes[i] == attributes[k]:
                        raise RAParserError(f'duplicate attribute {attributes[i]}', 0)
                    if attributes[i].lower() == attributes[k].lower():
                        raise RAParserError(f'duplicate attribute {attributes[i]}={attributes[k]}', 0)

        # store
        self.relation: str | None = relation
        self.attributes: list[str] | None = attributes

    def __str__(self) -> str:
        if self.relation is not None and self.attributes is None:
            return self.relation
        elif self.relation is None and self.attributes is not None:
            return f'({", ".join(self.attributes)})'
        else:
            return f'{self.relation}({", ".join(self.attributes)})'
