import os
import hashlib
import binascii
import functools

toast = ''

# TODO: change in production
HOST = 'localhost'
USERNAME = os.environ['DB_USER']
PASSWORD = os.environ['DB_PASS']
DATABASE = 'wsgi_app'
# TODO: change max pool to 50
connections = psycopg2.pool.ThreadedConnectionPool(1, 1,
                                                   host=HOST,
                                                   usernamesowe=USERNAME,
                                                   passwd=PASSWORD,
                                                   database=DATABASE)
current_user = None


def query_to_dict(query):
    return {d.split('=')[0]: d.split('=')[1]
            for d in query.split('&') if d}


def read_static(file_name, **kwargs):
    content = open(os.path.join(os.path.dirname(__file__),
                                f'../static/{file_name}'), 'rt').read()
    import pprint
    if file_name == 'html/base.html':
        if 'head' not in kwargs:
            kwargs['head'] = ''
        global toast
        kwargs['toast'] = ''
        if toast:
            kwargs['toast'] = f'<div class=\'toast toast-error\'>{toast}</div>'
            toast = ''
    # TODO: move the css/js to the static server
    if 'html' not in file_name:
        return content
    return content.format(**kwargs)


def resp_headers(content_length, content_type='text/html', **kwargs):
    headers = [('Content-Type', content_type),
               ('Content-Length', content_length)]
    if 'cookie' in kwargs:
        headers.append(('Set-Cookie', cookie))
    return headers


def redirect_headers(url, cookie=None):
    headers = [('Location', url)]
    if cookie:
        headers.append(('Set-Cookie', cookie))
    return headers


def hash_value(value):
    '''Hash a value for storing.'''
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', value.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_value(stored_value, provided_value):
    '''Verify a stored value against one provided by user'''
    salt = stored_value[:64]
    stored_value = stored_value[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_value.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_value
