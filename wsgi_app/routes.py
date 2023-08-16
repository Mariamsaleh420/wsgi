from .__main__ import MAPPER


@MAPPER.add(route='/', code=200)
def index(env):
    if env.get('HTTP_COOKIE') and 'login' in env.get('HTTP_COOKIE'):
        status = '302 FOUND'
        return status, utils.redirect_headers('/dashboard'), ''
    content_type = 'text/html'
    content = utils.read_static(
        'html/base.html', body=utils.read_static('html/index.html'))
    return status, utils.resp_headers(str(len(content))), content


@MAPPER.add(route='/register', request='post')
def register(env):
    con = utils.connections.getconn()
    cur = con.cursor()
    cookie = ''
    post_request = utils.query_to_dict(
        env['wsgi.input'].read().decode('utf-8'))
    new_user_sql = '''
            insert into users (email, username, password)
            values (%s, %s, %s) returning id, email,  username;
        '''
    new_user_data = (post_request['email'],
                     post_request['username'],
                     utils.hash_value(post_request['password']))
    cur.execute(new_user_sql, new_user_data)
    user = cur.fetchone()
    cookie = utils.hash_value(user[1])
    cur.execute(f'''insert into login_tokens
                    (token, user_id, user_agent)
                    values (\'{cookie}\', \'{user[0]}\',
                    \'{env["HTTP_USER_AGENT"]}\')''')
    con.commit()
    cookie = f'login = {cookie}'
    con.commit()
    cur.close()
    utils.connections.putconn(con)
    status = '302 FOUND'
    return status, utils.redirect_headers('/dashboard', cookie=cookie), ''


@MAPPER.add(route='/login', request='post')
def login(env):
    con = utils.connections.getconn()
    cur = con.cursor()
    post_request = utils.query_to_dict(
        env['wsgi.input'].read().decode('utf-8'))
    new_user_sql = 'select id, username, password from user_account where username=%s;'
    new_user_data = [post_request['username']]
    cur.execute(new_user_sql, new_user_data)
    user = cur.fetchone()
    url = '/'
    cookie = None
    if user:
        if utils.verify_value(user[2], post_request['user_password']):
            cookie = utils.hash_value(user[1])
            cur.execute(f'''insert into login_token
                            (token, user_account_id, user_agent)
                            values (\'{cookie}\', \'{user[0]}\',
                            \'{env["HTTP_USER_AGENT"]}\')''')
            con.commit()
            cookie = f'login = {cookie}'
            url = '/dashboard'
        else:
            utils.toast = 'wrong password'
    else:
        utils.toast = 'wrong username'
    cur.close()
    utils.connections.putconn(con)
    status = '302 FOUND'
    return status, utils.redirect_headers(url, cookie=cookie), ''


@MAPPER.add(route='/dashboard')
def dashboard(env):
    if env.get('HTTP_COOKIE') and 'login' in env.get('HTTP_COOKIE'):
        if not utils.current_user:
            con = utils.connections.getconn()
            cur = con.cursor()
            http_cookies = utils.query_to_dict(env.get('HTTP_COOKIE'))
            cur.execute(f'''
                    select u.id, u.email, u.username from login_tokens lt
                    left outer join users u on lt.user_id=u.id
                    where lt.token = '{http_cookies['login']}'
                    and lt.user_agent = '{env['HTTP_USER_AGENT']}'
                    ''')
            user = cur.fetchone()
            if user:
                utils.current_user = user
            else:
                utils.connections.putconn(con)
                utils.toast = 'please login'
                status = '302 FOUND'
                return status, utils.redirect_headers('/', cookie='login=\'\'; Expires=Wed, 21 Oct 2015 07:28:00 GMT'), ''
            utils.connections.putconn(con)
        status = '200 OK'
        content_type = 'text/html'
        context = {
            'username': utils.current_user[0],
            'team': utils.current_user[1],
        }
        content = utils.read_static(
            'html/base.html',
            head='<script src=\'static\script.js\' async></script>',
            body=utils.read_static('html/dashboard.html', **context)
        )
        return status, utils.resp_headers(str(len(content))), content
    utils.toast = 'please login'
    status = '302 FOUND'
    return status, utils.redirect_headers('/', cookie='login=\'\'; Expires=Wed, 21 Oct 2015 07:28:00 GMT'), ''


@MAPPER.add(route='/static/*')
def serve_static(env):
    file_name = env['PATH_INFO'].split('/').pop()
    content = utils.read_static(file_name)
    content_type = 'text/css' if '.css' in file_name else 'application/javascript'
    return '200 OK', utils.resp_headers(str(len(content)), content_type=content_type), content
import os

from .__main__ import MAPPER


@MAPPER.add(code=404)
def not_found(env):
    status = '404 NOT FOUND'
    content_type = 'text/html'
    content = utils.read_static(
        'html/base.html', body=utils.read_static('html/page_not_found.html'))
    return status, utils.resp_headers(str(len(content))), content


@MAPPER.add(code=403)
def forbidden(env):
    if env['REQUEST_METHOD'].lower() == 'post':
    utils.toast = 'this url only accepts post requests'
    status = '403 FORBIDDEN'
    content = utils.read_static(
        'html/base.html', body=utils.read_static('html/forbidden.html'))
    return status, utils.resp_headers(str(len(content))), content

    return '403 FORBIDDEN', utils.resp_headers(str(len(content)), content_type='application/json'), content


@MAPPER.add(code=500)
def internal_server_error(env):
    status = '500 INTERNAL SERVER ERROR'
    content_type = 'text/html'
    errors = ''
    if os.environ.get('DEBUG', ''):
        import traceback
        errors = traceback.format_exc()
        print("[\033[1;31mERROR\033[0m]\t", end='', flush=True)
        print(errors)
    content = utils.read_static(
        'html/base.html', body=utils.read_static('html/internal_server_error.html',
                                                 errors=errors))
    return status, utils.resp_headers(str(len(content))), content
