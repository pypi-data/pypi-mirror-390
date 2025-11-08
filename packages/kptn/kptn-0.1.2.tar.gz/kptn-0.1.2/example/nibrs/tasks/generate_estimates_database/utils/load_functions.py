import logging
import pandas as pd
import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        logging.debug(f"Time taken for {func.__name__}: {total_time} seconds")
        return result, total_time

    return wrapper


def load_into_database(
    data: list, db, new_table_name: str, columns: list
) -> tuple[dict, float]:
    """Insert data into the database."""
    insert_query = prepare_bulk_insert_query(new_table_name, columns)
    try:
        results, total_time = insert_data_to_db(db, insert_query, data)
        return results, total_time
    except Exception as e:
        print(f"Database error: {e}")
        raise


def select_and_convert_columns(filtered_df, columns_and_types):
    columns = list(columns_and_types.keys())
    df_selected = filtered_df[columns].copy()
    for column, dtype in columns_and_types.items():
        try:
            if dtype == "bool":
                df_selected.loc[:, column] = df_selected[column].astype("bool")
            elif dtype == "string":
                df_selected.loc[:, column] = df_selected[column].astype("string")
            elif dtype == "int":
                df_selected.loc[:, column] = df_selected[column].astype("int")
            elif dtype == "float":
                df_selected.loc[:, column] = (
                    df_selected[column].round(4).astype("float")
                )
            else:
                df_selected.loc[:, column] = df_selected[column].astype(dtype)
        except FutureWarning as e:
            column_type = type(df_selected.loc[:, column])
            logging.info(
                f"Warning setting {column} of default_type: {column_type} to dtype: {dtype}"
            )
    return df_selected


def prepare_bulk_insert_query(new_table_name, columns):
    insert_query = f"""
        INSERT INTO {new_table_name} ({', '.join(columns)})
        VALUES %s
    """
    logging.debug(f"Insert query: {insert_query}")
    return insert_query


@measure_time
def insert_data_to_db(db_manager, insert_query, data, batch_size=1000):
    starting_row = 0
    data_length = len(data)
    file_rows_written_to_db = 0
    failed_rows = 0

    while starting_row < data_length:
        logging.debug(f"Starting row: {starting_row}")
        if starting_row + batch_size > data_length:
            batch_size = len(data) - starting_row

        data_batch = data[starting_row : starting_row + batch_size]
        values_list = []
        flattened_batch = []

        for row in data_batch:
            cleaned_row = [None if pd.isna(value) else value for value in row]
            values_str = "(" + ", ".join(["%s"] * len(cleaned_row)) + ") "
            values_list.append(values_str)
            flattened_batch.extend(cleaned_row)

        values_clause = ", ".join(values_list)
        query = insert_query % values_clause

        rows_written = db_manager.insert_data_with_query(query, flattened_batch)
        file_rows_written_to_db += rows_written
        failed_rows += len(data_batch) - rows_written

        if len(data_batch) - rows_written > 0:
            logging.error(f"Failed rows: {insert_query} values: {flattened_batch}")

        starting_row += batch_size

    results = {
        "file_rows_written_to_db": file_rows_written_to_db,
        "failed_rows": failed_rows,
    }
    return results
