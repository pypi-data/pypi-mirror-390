from typing import Tuple, Dict

from .. import RARelationReference
from ..LogicElement import LogicElement
from ..RAElement import RAElement
from ..RAUnaryOperator import RAUnaryOperator
from ...ParserError import RAParserError
from ...tokenizer import Token
from ...util.RenamableColumnList import RenamableColumnList
from ....db import Table


class Rename(RAUnaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return 'ρ', 'ϱ', 'rho'

    @classmethod
    def parse_args(cls: type[RAUnaryOperator], *tokens: Token, depth: int):
        from .. import RARelationReference
        return RARelationReference.parse_tokens(cls, *tokens, depth=depth)

    def __init__(self, target: RAElement, arg: RARelationReference):
        super().__init__(target)
        self.reference: RARelationReference = arg

    @property
    def arg(self) -> LogicElement:
        return self.reference

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subquery
        subquery, subcols = self.target.to_sql(tables)

        # rename attributes
        if self.reference.relation is None and self.reference.attributes is not None:
            return self._to_sql_with_renamed_attributes(tables, subquery, subcols)

        # rename relation
        elif self.reference.relation is not None and self.reference.attributes is None:
            return self._to_sql_with_renamed_relation(tables, subquery, subcols)

        # rename relation and attributes
        else:
            return self._to_sql_with_renamed_relation_and_attributes(tables, subquery, subcols)

    def _to_sql_with_renamed_relation(self,
                                      tables: Dict[str, Table],
                                      subquery: str,
                                      subcols: RenamableColumnList) -> Tuple[str, RenamableColumnList]:
        # check if there are two columns with the same name
        for i in range(len(subcols)):
            for k in range(i + 1, len(subcols)):
                if subcols[i].name == subcols[k].name:
                    raise RAParserError(
                        f'attribute {subcols[i].name} is present in both {subcols[i].table.name} and {subcols[k].table.name}',
                        depth=0
                    )

        # add new table
        table = Table(self.reference.relation)
        # tables[self.reference.relation] = table

        # set table for all attributes
        for col in subcols:
            col.table = table

        # return
        return subquery, subcols

    def _to_sql_with_renamed_attributes(self,
                                        tables: Dict[str, Table],
                                        subquery: str,
                                        subcols: RenamableColumnList) -> Tuple[str, RenamableColumnList]:
        # check if there are more names than subcols
        if len(self.reference.attributes) > len(subcols):
            raise RAParserError('more names than attributes', 0)

        # rename columns
        for col, new_name in zip(subcols, self.reference.attributes):
            col.name = new_name

        # return
        return subquery, subcols

    def _to_sql_with_renamed_relation_and_attributes(self,
                                                     tables: Dict[str, Table],
                                                     subquery: str,
                                                     subcols: RenamableColumnList) -> Tuple[str, RenamableColumnList]:
        subquery, subcols = self._to_sql_with_renamed_attributes(tables, subquery, subcols)
        subquery, subcols = self._to_sql_with_renamed_relation(tables, subquery, subcols)

        return subquery, subcols
