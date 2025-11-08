import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from tasks.generate_estimates_database.utils.config import logger

class DatabaseManager:
    def __init__(self, host, port, dbname, user, password):
        if not password or password == "":
            logger.error("PGPASSWORD environment variable not set")
            raise Exception("Please set PGPASSWORD environment variable")
        elif not all([host, port, dbname, user, password]):
            logger.error(
                "All parameters (host, port, user, password, database_name) must be provided."
            )
            raise Exception(f"All parameters ({host}, {port}, {user}, [password], {dbname}) must be provided.")
        else:
            self.params = {
                "host": host,
                "port": port,
                "dbname": dbname,
                "user": user,
                "password": password,
                "keepalives": 1,
                "keepalives_idle": 1200,
                "keepalives_interval": 5,
                "keepalives_count": 5,
            }

    def connect(self):

        return psycopg2.connect(**self.params)

    def run_sql(self, sql, fetch_all=False, fetch_one=False, header=False):
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if fetch_one:
                        result = cur.fetchone()
                        if header:
                            if result:
                                # Get column names from cursor description
                                colnames = [desc[0] for desc in cur.description]
                                # Combine column names with row values
                                result_dict = dict(zip(colnames, result))
                                return result_dict
                        return result

                    if fetch_all:
                        return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"An error occurred while executing SQL: {str(e)}")
            raise e

    def insert_data_with_query(self, query, flattened_batch):
        conn = None
        for x in range(5):
            try:
                with self.connect() as conn:
                    with conn.cursor() as cur:
                        formatted_query = cur.mogrify(query, flattened_batch).decode(
                            "utf-8"
                        )
                        cur.execute(query, flattened_batch)
                        conn.commit()
                        rows_written = cur.rowcount
                        return rows_written
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                logger.error(
                    f"Database Connection [InterfaceError or OperationalError]: {str(e)}"
                )
                if conn:
                    conn.rollback()
            except psycopg2.Error as e:
                logger.error(f"An error occurred while executing SQL: {str(e)}")
                if conn:
                    conn.rollback()
                raise e
            finally:
                if conn:
                    conn.close()
        raise Exception("Failed to insert data after 5 attempts")

    def db_exists(self, dbname: str) -> bool:
        """
        Check if a given PostgreSQL database exists.

        :param dbname: Name of the database to check.
        :return: True if the database exists, otherwise False.
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    # Use EXISTS(...) for a direct boolean result
                    cur.execute(
                        "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = %s)",
                        (dbname,),
                    )
                    result = cur.fetchone()
                    if result is None:
                        return False
                    exists = result[0]
                    return bool(exists)
        except psycopg2.Error as e:
            logger.exception(
                f"An error occurred while checking if database '{dbname}' exists: {str(e)}"
            )
            return False

    def table_exists(self, table_name) -> bool:
        try:
            # Connect to the database server
            logger.info(
                f"Connecting to '{self.params['dbname']}' db to see if table '{table_name}' exists..."
            )
            with self.connect() as conn:
                result = False
                # Check if the table already exists
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s",
                        (table_name,),
                    )
                    result = bool(cur.fetchone())
                    logger.debug(
                        f"SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}' returned: {result}"
                    )

                return result

        except psycopg2.Error as e:
            logger.error(f"An error occurred while checking for the table: {str(e)}")
            return e

    def create_database(self, new_db_name):
        """
        Create a PostgreSQL database with the given parameters.
        :param new_db_name: Name of the database to create
        """
        conn = None
        try:
            conn = self.connect()
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {new_db_name}")
                logger.info(f"Database '{new_db_name}' created successfully.")

        except psycopg2.DatabaseError as error:
            logger.error(f"Database error occurred: {error}")
            raise Exception(f"Database error occurred: {error}")
        except psycopg2.Error as e:
            logger.error(
                f"An error occurred while creating the database '{new_db_name}': {str(e)}"
            )
            raise e
        except Exception as error:
            logger.exception(f"An unexpected error occurred: {error}")
            raise Exception(f"An unexpected error occurred: {error}")
        finally:
            if conn:
                conn.close()
