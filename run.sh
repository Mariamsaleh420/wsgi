#!/bin/sh

OK='[\033[1;32mOK\033[0m]\t'
WARN='[\033[1;33mWARN\033[0m]\t'
ERROR='[\033[1;31mERROR\033[0m]\t'
RUNNING="\033[1;33m __  ___ __  __  ______  ______  __  ______  ______
/\ \/ ___\ \/\ \/\  __ \/\  __ \/\ \/\  __ \/\  __ \\
\ \  /___/\ \_\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \_\ \\
 \ \_\   \ \_____\ \_\ \ \ \_\ \ \ \_\ \_\ \_\ \___  \\
  \/_/    \/_____/\/_/\/_/\/_/\/_/\/_/\/_/\/_/\/___/\ \\
 __________________________________________________\_\ \\
/\______________________________________________________\\
\/______________________________________________________/\033[0m"

assert() {
    exit_code="$?"
    [ "$exit_code" = 0 ] && ([ -z "$1" ] || echo "$OK$1") || (
    [ -z "$2" ] || echo "$ERROR$2 - exit code:$exit_code")
}

[ -f ./env.sh ] && . ./env.sh
assert '' 'you need to do the setup? see usage'

case "${1:-'usage'}" in
    run-dev-server)
        echo "$RUNNING"
        echo "${WARN}server at http://localhost:8000"
        . ./venv/bin/activate
        hypercorn --workers 1 --reload --debug --graceful-timeout 1\
            --error-logfile - --worker-class asyncio \
            webment_focus_server.asgi_dev:app
        assert 'server exited successfully' 'server failed on exit' ;;

    run-pro-server)
        echo "$RUNNING"
        echo "${WARN}server at http://localhost:5000"
        uwsgi -p 1 --py-autoreload 1 --http :5000 -H $PWD/venv \
            --chdir webment_focus_server --wsgi-file pro_wsgi.py
        assert 'server exited successfully' 'server failed on exit' ;;

    populate-db)
        echo "$RUNNING"
        echo 'populating'
        (exit 20)
        assert 'database populated' 'error inserting the database dump' ;;

    run-tests)
        echo "\033[1;33m  ___                        ___
 /\  \                      /\  \
 \_\  \___                  \_\  \___
/\___   __\  ______    ____/\___   __\  __  ______  ______
\/_/ \  \_/ /\  __ \  /  __\/_/ \  \_/ /\ \/\  __ \/\  __ \
    \ \  \__\ \ \_\_\/\__,  \  \ \  \__\ \ \ \ \ \ \ \ \_\ \
     \ \_____\ \_____\/\____/   \ \_____\ \_\ \_\ \_\ \___  \
      \/_____/\/_____/\/___/     \/_____/\/_/\/_/\/_/\/___/\ \
 _________________________________________________________\_\ \
/\_____________________________________________________________\
\/_____________________________________________________________/\033[0m\t"
        echo "${WARN}feeding database from ${SCHEMA}"
        mysql -uroot -p${DB_PASS} ${DB} < ${SCHEMA}
        assert "database is full" "database is still hungry"
        echo "${WARN}create database ${DB}_test"
        mysql -uroot -p${DB_PASS} -e "create database ${DB}_test;"
        assert "database created" "creation failed"
        echo "${WARN}feeding database from ${SCHEMA}"
        mysql -uroot -p${DB_PASS} ${DB}_test < ${SCHEMA}
        assert "database is full" "database is still hungry"
        echo "${WARN}running tests"
        #python3 -m tests
        echo "${WARN}dropping database"
        mysql -uroot -p${DB_PASS} -e "drop database ${DB}_test;"
        assert "database dropped" "dropping failed" ;;
        ;;

    do-setup)
        echo "${OK}pussy"
        echo "$RUNNING"
        echo "${WARN}creating virtual enviroment"
        python3 -m venv venv
        . ./venv/bin/activate
        assert 'venv created' 'do you have python3.8.X installed?'
        echo "${WARN}installing dependecies"
        pip install -r requirements.txt
        assert 'libs installed' 'send hassona the output above'
        echo "${WARN}creating enviroment variables"
        touch env.sh
        echo "${WARN}test: \c" && read test
        echo "#!/bin/sh
export test=$test
" > ./env.sh
        assert 'while you where sitting on your ass i did everything you lil shit'\
            'WHAT DID YOU DO! YOU FAILED! YOU ARE A FAILURE! YOU ALWAYS FAIL!';;
    usage)
        echo "${WARN}Usage: ./manage.sh [OPTIONS]

OPTIONS:
- run-dev-server: for hardcore backend coders to see their code at action
- run-pro-server: for production and frontend coders
- populate-db: builds the database schema
- run-tests: functionality testing for the api
- do-setup: for hagora l 2moura
- usage\n" ;;

    *)
        echo "${ERROR}Usage: ./manage.sh usage" ;;
esac
