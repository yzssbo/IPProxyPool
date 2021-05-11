#!/usr/bin/env bash

declare -r CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
declare -r ROOT_PATH=$(dirname "${CUR_PATH}")
declare -r APEND_PATH=$(dirname "${ROOT_PATH}")
declare -r LOG_DIR_PATH="${ROOT_PATH}/logs"
declare -r UWSGI_INI="${ROOT_PATH}/uwsgi.ini"
declare -r UWSGI_PID="${ROOT_PATH}/bin/uwsgi.pid"
declare -r LOG_FILE="${LOG_DIR_PATH}/run.log"

source $HOME/Venv/ip/bin/activate

export PYTHONPATH="${APEND_PATH}":$PYTHONPATH

function show_error()
{
    local -r msg=$1
    echo "[ERROR] ${msg}"
}

function usage()
{
    local -r usage="Usage: $BASH_SOURCE start|stop|restart"
    echo "${usage}"

return 0
}

function start()
{
    nohup uwsgi --ini ${UWSGI_INI} 2>&1 1>${LOG_FILE} &
    if [ 0 -ne $? ];then
        show_error "FAIL to start uwsgi !"
        return 1
    fi

return 0
}

function stop()
{
    uwsgi --stop ${UWSGI_PID}  2>&1 1>${LOG_FILE}
    return 0
}

function restart()
{
    uwsgi --reload ${UWSGI_PID}  2>&1 1>${LOG_FILE}
    if [ 0 -ne $? ];then
        return 1
    fi
    return 0
}

function main()
{
    local -r opt=$1
    if [ -z ${opt} ];then
        usage
        return 1
    fi

    if [ 'start' == ${opt} ]
    then
        start
        return $?
    elif [ 'stop' == ${opt} ]
    then
        stop
        return $?
    elif [ 'restart' == ${opt} ]
    then
        restart
        return $?
    else
        usage
        return 1
    fi

return 0
}

main $@

