import io
import json

from sowescrum import routes

test_count = 0

OK = "[\033[1;32mOK\033[0m]\t"
WARN = "[\033[1;33mWARN\033[0m]\t"
ERROR = "[\033[1;31mERROR\033[0m]\t"


STATUS_200 = '200 OK'
STATUS_302 = '302 FOUND'
STATUS_403 = '403 FORBIDDEN'
STATUS_404 = '404 NOT FOUND'
STATUS_500 = '500 INTERNAL SERVER ERROR'


def send_request(test_name, route, env, status, redirect=None):
    global test_count
    url_status, resp_headers, _ = routes.router[route](env)
    fail_text = (f'test \'{test_name}\' failed at route \'{route}\' ' +
                 f'status {url_status} not {status}')
    pass_text = f'{OK}test \'{test_name}\' {status.split()[0]} passed at \'{route}\''
    if env.get('HTTP_COOKIE'):
        fail_text += f' with cookie {env["HTTP_COOKIE"]}'
        pass_text += f' with cookie {env["HTTP_COOKIE"]}'
    if env.get('wsgi.input'):
        wsgi_input = routes.utils.query_to_dict(
            env['wsgi.input'].reader.getvalue().decode('utf-8')
        )
        fail_text += f' for wsgi.input {wsgi_input}'
    assert url_status == status, fail_text
    test_count += 1
    print(pass_text)
    url = resp_headers[0][1]
    if redirect:
        fail_text = (f'test \'{test_name}\' failed at route \'{route}\' ' +
                     f'redirect to \'{url}\' not \'{redirect}\'')
        pass_text = f'{OK}test \'{test_name}\' at \'{route}\' redirected to \'{redirect}\''
        if env.get('HTTP_COOKIE'):
            fail_text += f' with cookie {env["HTTP_COOKIE"]}'
            pass_text += f' with cookie {env["HTTP_COOKIE"]}'
        if env.get('wsgi.input'):
            wsgi_input = routes.utils.query_to_dict(
                env['wsgi.input'].reader.getvalue().decode('utf-8')
            )
            fail_text += f' for wsgi.input {wsgi_input}'
        assert url == redirect, fail_text
        test_count += 1
        print(pass_text)


def api_send_request(test_name, route, env, status, json_test):
    global test_count
    api_status, _, json_content = routes.router[route](env)
    fail_text = (f'test \'{test_name}\' failed at route \'{route}\' ' +
                 f'status {api_status} not {status} ' +
                 f'for json {json_test}')
    pass_text = f'{OK}test \'{test_name}\' {status.split()[0]} passed at \'{route}\''
    if env.get('HTTP_COOKIE'):
        fail_text += f' with cookie {env["HTTP_COOKIE"]}'
        pass_text += f' with cookie {env["HTTP_COOKIE"]}'
    assert api_status == status, fail_text
    test_count += 1
    print(pass_text)
    fail_text = (f'test \'{test_name}\' failed at route \'{route}\' ' +
                 f'json is {json_content} not {json_test}')
    pass_text = f'{OK}test \'{test_name}\' {json_test} passed at \'{route}\''
    if env.get('HTTP_COOKIE'):
        fail_text += f' with cookie {env["HTTP_COOKIE"]}'
        pass_text += f' with cookie {env["HTTP_COOKIE"]}'
    assert json_content == json.dumps(json_test), fail_text
    test_count += 1
    print(pass_text)
