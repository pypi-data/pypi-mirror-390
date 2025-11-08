import sqlglot


class InvalidQueryError(Exception):
    pass


def safe_sql(sql_query, read: str | None = None):
    """Return SQL statement or raise if not a valid SELECT statement"""
    read = read or "mysql"
    if not sql_query:
        raise InvalidQueryError("Empty statement found.")
    try:
        parsed_statements = sqlglot.parse(sql_query, read=read)
    except sqlglot.errors.ParseError as e:
        raise InvalidQueryError(f"SQL parsing failed: {e}") from e
    else:
        if not parsed_statements:
            raise InvalidQueryError("Query string is empty or invalid.")
        for statement in parsed_statements:
            if not isinstance(statement, sqlglot.exp.Query):
                if statement:
                    raise InvalidQueryError(
                        "Forbidden statement type found: "
                        f"{statement.__class__.__name__}. "
                        "Only read-only queries are allowed."
                    )
                raise InvalidQueryError("Invalid or empty statement found.")
    return sql_query
