from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..RABinaryOperator import RABinaryOperator
from ...ParserError import RAParserError
from ...util.RenamableColumnList import RenamableColumnList


class LeftSemiJoin(RABinaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return chr(8905), 'lsjoin'

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subqueries
        lq, lcols = self.left.to_sql(tables)
        rq, rcols = self.right.to_sql(tables)

        # find matching columns
        join_cols, all_cols = lcols.intersect(rcols)
        if len(join_cols) == 0:
            raise RAParserError('no common attributes found for left semi join', 0)

        on_clause = ' AND '.join(f'{l.current_name} = {r.current_name}' for l, r in join_cols)

        # create sql
        return f'SELECT DISTINCT {lcols.list} FROM ({lq}) {self._name()} JOIN ({rq}) {self._name()} ON {on_clause}', lcols
