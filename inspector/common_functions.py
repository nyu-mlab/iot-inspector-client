import sqlite3


def insert_many(db_conn, target_table_name, dict_list):
    """
    Shortcut for inserting one or multiple rows into a database.

    Example:

        Instead of doing this...
            db_conn.insert_many(
                'INSERT INTO mytable(k1, k2) VALUES (?, ?)',
                [(1, 2), (3, 4)]
            )

        we can do this equivalently...
            insert_many(db_conn, 'mytable', [
                {'k1': 1, 'k2': 2},
                {'k1': 3, 'k2': 4},
            ])

    """
    if len(dict_list) == 0:
        return

    # Get all the column names
    col_set = set()
    for input_dict in dict_list:
        col_set |= set(input_dict.keys())

    col_list = sorted(col_set)

    # Rearrange all the inserted data according to column names
    insert_list = []
    for input_dict in dict_list:
        insert_list.append(tuple([
            input_dict.setdefault(col, None) for col in col_list
        ]))

    # Make sql
    sql = f'INSERT INTO {target_table_name} ('
    sql += ', '.join(col_list)
    sql += ') VALUES ('
    sql += ', '.join(['?'] * len(col_list)) + ')'

    try:
        return db_conn.executemany(sql, insert_list)
    except sqlite3.OperationalError:
        print('Error in SQL query:')
        print(sql)
        raise


def round_down(input_number, mod_n):
    """
    Round down a number the highest multiples of mod_n that is less than the
    number.

    For example, round_down(23, 10) == 20

    """
    input_number = int(input_number)

    return input_number - (input_number % mod_n)


