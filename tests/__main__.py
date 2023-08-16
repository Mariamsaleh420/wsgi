import copy
import io
import sys
import json
import datetime


import psycopg2.pool
import gunicorn.http


from . import utils
from sowescrum import routes

START_TIME = datetime.datetime.now()  # nopep8

routes.utils.connections = psycopg2.pool.ThreadedConnectionPool(
    1, 1, database='sowescrum-test')
con = routes.utils.connections.getconn()
cur = con.cursor()
cur.execute('''
        insert into login_token (token, user_account_id, user_agent)
        values (\'faketoken\', \'1\', \'user agent\');''')
con.commit()
routes.utils.connections.putconn(con)

ENV_GET = {'REQUEST_METHOD': 'get'}
ENV_STATIC = {**ENV_GET, 'PATH_INFO': '/static/spectre.min.css'}
ENV_LOGIN_TOKEN = {
    **ENV_GET,
    'HTTP_COOKIE': 'login=faketoken', 'HTTP_USER_AGENT': 'user agent'
}

ENV_POST_TEMP = {'REQUEST_METHOD': 'post',
                 'HTTP_USER_AGENT': 'user agent'}
ENV_POST = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'name=testteam&team_password=password&username=testname&' +
            b'user_password=testpass'
        )
    )
}
ENV_POST_TEAM = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'name=testteam1&team_password=password&username=' +
            b'testname&user_password=testpass'
        )
    )
}
ENV_POST_TEAM_PASS = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'name=testteam&team_password=1password&username=' +
            b'testname&user_password=testpass'
        )
    )
}
ENV_POST_USER = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'name=testteam&team_password=password&username=1testname&' +
            b'user_password=testpass'
        )
    )
}
ENV_POST_USER_NAME = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'username=wrongtestname&user_password=testpass'
        )
    )
}
ENV_POST_USER_PASS = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(
            b'username=testname&user_password=wrongtestpass'
        )
    )
}

TEST_NAME = (
    *('unauthroized method',)*3,
    'page not found',
    'internal server error',
    'index',
    'dashboard',
    'static file',
    *('token',)*2,
    'register team',
    'used teamname',
    'used username',
    'wrong team name',
    'wrong team password',
    'used username',
    'register user',
    'login user',
    'wrong username',
    'wrong password'
)
ROUTE = (
    '/register_team',
    '/register_user',
    '/login',
    404,
    500,
    '/',
    '/dashboard',
    '/static/*',
    '/',
    '/dashboard',
    *('/register_team',)*3,
    *('/register_user',)*4,
    *('/login',)*3,
)
ROUTE_ENV = (
    *(ENV_GET,)*7,
    ENV_STATIC,
    *(ENV_LOGIN_TOKEN,)*2,
    *(ENV_POST,)*2,
    *(ENV_POST_TEAM,)*2,
    ENV_POST_TEAM_PASS,
    ENV_POST,
    *(ENV_POST_USER,)*2,
    ENV_POST_USER_NAME,
    ENV_POST_USER_PASS,
)
ROUTE_STATUS = (
    *(utils.STATUS_403,)*3,
    utils.STATUS_404,
    utils.STATUS_500,
    utils.STATUS_200,
    utils.STATUS_302,
    utils.STATUS_200,
    utils.STATUS_302,
    utils.STATUS_200,
    *(utils.STATUS_302,)*10,
)
ROUTE_REDIRECTS = (
    *(None,)*6,
    '/',
    None,
    '/dashboard',
    None,
    '/dashboard',
    *('/',)*5,
    *('/dashboard',)*2,
    *('/',)*2,
)

ENV_POST_PROJECT = {
    **ENV_POST_TEMP,
    'wsgi.input': gunicorn.http.body.Body(
        io.BytesIO(b'project_name=testname')
    )
}

API_TEST_NAME = (
    'get test',
    *('post test',)*2,
)
API_ROUTE = (
    '/api/new_project',
    '/api/new_project',
)
API_ROUTE_ENV = (
    ENV_GET,
    ENV_POST_PROJECT,
)
API_ROUTE_STATUS = (
    utils.STATUS_403,
    utils.STATUS_200,
)
API_ROUTE_JSON = (
    {},
    {'feedback': True},
)


TEST_TOTAL = (len(ROUTE)+len(API_ROUTE)*2 +
              len([r for r in ROUTE_REDIRECTS if r]))
try:
    list(map(utils.send_request,
             TEST_NAME,
             ROUTE,
             ROUTE_ENV,
             ROUTE_STATUS,
             ROUTE_REDIRECTS))
    list(map(utils.api_send_request,
             API_TEST_NAME,
             API_ROUTE,
             API_ROUTE_ENV,
             API_ROUTE_STATUS,
             API_ROUTE_JSON))

except Exception as e:
    import traceback
    print(traceback.format_exc())
    print(f'{utils.ERROR}{e}', end='')
    exit_code = 1
else:
    print(f'{utils.OK}tests passed', end='')
    exit_code = 0
print(f' | {utils.test_count}/{TEST_TOTAL} tests done | test time = {datetime.datetime.now()-START_TIME}')
sys.exit(exit_code)
