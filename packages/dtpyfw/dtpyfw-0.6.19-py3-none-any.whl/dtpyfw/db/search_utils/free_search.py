"""Free-text search condition builder for PostgreSQL.

Provides functions to build WHERE conditions and ORDER BY clauses for
full-text search using PostgreSQL's text search capabilities and
similarity functions.
"""

from typing import Sequence, Tuple

from sqlalchemy import String, Text, cast, desc, func, literal, or_
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression
from sqlalchemy.sql.functions import Function


def free_search(
    columns: Sequence[ColumnElement],
    query: str,
    threshold: float,
    exact: bool = True,
    tokenize: bool = True,
) -> Tuple[Sequence[ColumnElement], Sequence[UnaryExpression]]:
    """Build WHERE conditions and ORDER BY clauses for a free-text search.

    Creates SQL conditions and sorting expressions for searching across multiple
    columns using PostgreSQL full-text search and similarity functions. Supports
    exact phrase matching, fuzzy matching, and tokenized search.

    Args:
        columns: List of SQLAlchemy column expressions to search.
        query: The search string entered by the user.
        threshold: Minimum similarity score (0.0-1.0) for fuzzy matching.
        exact: If True, perform exact phrase matching; otherwise, fuzzy matching.
        tokenize: If True, use PostgreSQL full-text search; otherwise, use simple
            string comparison or similarity.

    Returns:
        A tuple (conditions, order_by) where:
            - conditions: List of SQL boolean expressions for WHERE clause.
            - order_by: List of SQL expressions for ORDER BY clause (relevance ranking).
    """
    # Helper: cast query to Text
    txt_query = literal(query).cast(Text)
    def similarity_expressions() -> Sequence[Function]:
        return [func.similarity(cast(col, Text), txt_query) for col in columns]

    # Non-tokenized logic
    if not tokenize:
        if exact:
            low = query.lower()
            exprs = [func.lower(cast(col, Text)) == low for col in columns]
            return [or_(*exprs)], []
        sims = similarity_expressions()
        best = func.greatest(*sims)
        return [best > threshold], [desc(best)]

    # Tokenized logic: build TSVECTOR
    concatenated = func.concat_ws(" ", *[cast(col, String) for col in columns])
    tsv = func.to_tsvector(literal("english", type_=REGCONFIG), concatenated)

    if exact:
        tsq = func.phraseto_tsquery("english", query)
        rank = func.ts_rank_cd(tsv, tsq)
        return [tsv.op("@@")(tsq)], [desc(rank)]

    # Combined fuzzy + full-text
    tsq = func.websearch_to_tsquery("english", query)
    rank = func.ts_rank_cd(tsv, tsq)
    sims = similarity_expressions()
    best = func.greatest(*sims)
    combined = func.greatest(rank, best)
    cond = or_(tsv.op("@@")(tsq), best > threshold)
    return [cond], [desc(combined)]
