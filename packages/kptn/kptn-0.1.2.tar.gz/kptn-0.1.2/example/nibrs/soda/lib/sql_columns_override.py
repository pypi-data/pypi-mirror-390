# Override the default query for retrieving table columns
# For Postgres materialized views, we need to query pg_attribute instead of information_schema.columns
def sql_get_table_columns(
    self,
    table_name: str,
    included_columns: list[str] | None = None,
    excluded_columns: list[str] | None = None,
) -> str:
    table_name_default_case = self.default_casify_table_name(table_name)
    unquoted_table_name_default_case = (
        table_name_default_case[1:-1]
        if self.is_quoted(table_name_default_case)
        else table_name_default_case
    )

    schema = self.default_casify_system_name(self.schema)
    tableName = f"{schema}.{unquoted_table_name_default_case}"
    sql = (
        "SELECT attname AS column_name, format_type(atttypid, atttypmod) AS data_type \n"
        "FROM   pg_attribute \n"
        f"WHERE  attrelid = '{tableName}'::regclass \n"
        "AND NOT attisdropped \n"
        "AND attnum > 0 \n"
        "ORDER BY attnum;"
    )
    return sql
