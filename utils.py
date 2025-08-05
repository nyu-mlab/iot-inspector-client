import functools
import libinspector


@functools.lru_cache(maxsize=256)
def get_hostname(ip_address):
    db_conn, rwlock = libinspector.global_state.db_conn_and_lock
    with rwlock:
        result = db_conn.execute("SELECT * FROM hostnames WHERE ip_address = ?", (ip_address,))
        print(f'host information result for ip {ip_address}: {result}')
        for row in result:
            print(f'row: {row}')
        return result.fetchone()[0] if result.fetchone() else None