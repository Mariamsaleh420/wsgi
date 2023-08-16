import mysql.connector
from mysql.connector import pooling
import utils

CON_POOL = pooling.MySQLConnectionPool(
    pool_size=1,
    database='wsgi_app',
    user='root',
    password=os.environ['DB_PASS']
)

import routes  # nopep8


def application(env, resp):
    try:
        con = CON_POOL.get_connection()
        status, headers, content = MAPPER.route(env, con)
        cursor = con.cursor()
        while True:
            pass
        # TODO: con.close() close in the mapper
    except Exception:
        status, headers, content = MAPPER.abort(500)
        print('error')
    resp(status, headers)
    yield content.encode('utf8')
