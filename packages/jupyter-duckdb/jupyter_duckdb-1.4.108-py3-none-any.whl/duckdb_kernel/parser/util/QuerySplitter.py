from typing import Iterator


def split_queries(query: str, split_at: str | None = ';', remove_comments: bool = False) -> Iterator[str]:
    quotes = '\'"`'

    escaped = False
    in_quotes = None
    in_singleline_comment = False
    in_multiline_comment = False

    previous = None
    current_query = []

    for symbol in query:
        keep_symbol = True

        # escaped symbol
        if escaped:
            escaped = False

        # backslash (escape)
        elif symbol == '\\':
            escaped = True

        # if in quotes
        elif in_quotes is not None:
            if symbol == in_quotes:
                in_quotes = False

        # if in single line comment
        elif in_singleline_comment:
            if symbol == '\n':
                in_singleline_comment = False
            elif remove_comments:
                keep_symbol = False

        # if in multiline comment
        elif in_multiline_comment:
            if previous == '*' and symbol == '/':
                in_multiline_comment = False

            if remove_comments:
                keep_symbol = False

        # start of quotes
        elif symbol in quotes:
            in_quotes = symbol

        # start of single line comment
        elif previous == '-' and symbol == '-':
            in_singleline_comment = True

            if remove_comments:
                keep_symbol = False
                current_query.pop()

        # start of multiline comment
        elif previous == '/' and symbol == '*':
            in_multiline_comment = True

            if remove_comments:
                keep_symbol = False
                current_query.pop()

        # semicolon
        elif split_at is not None and symbol == split_at:
            yield ''.join(current_query)

            current_query = []
            keep_symbol = False

        # store symbol
        if keep_symbol:
            current_query.append(symbol)

        previous = symbol

    # yield remaining symbols
    yield ''.join(current_query)


def get_last_query(query: str, split_at: str | None = ';', remove_comments: bool = False) -> str:
    for query in split_queries(query, split_at, remove_comments):
        pass

    return query
