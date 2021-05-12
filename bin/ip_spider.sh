#!/usr/bin/env bash

declare -r CUR_PATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
declare -r ROOT_PATH=$(dirname "${CUR_PATH}")
declare -r APEND_PATH=$(dirname "${ROOT_PATH}")
declare -r LOG_DIR_PATH="${ROOT_PATH}/logs"
declare -r PYTHON_FILE="${ROOT_PATH}/async/ip_spider.py"
declare -r STOP_FILE="${ROOT_PATH}/async/__stop_ip_spider__"
declare -r LOG_FILE="${LOG_DIR_PATH}/shell_ip_spider.log"

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
    if [ -e "${STOP_FILE}" ];then
      rm -rf "${STOP_FILE}"
    fi

    nohup python ${PYTHON_FILE} 2>&1 1>${LOG_FILE} &
    if [ 0 -ne $? ];then
        show_error "FAIL to start ${PYTHON_FILE} !"
        return 1
    fi

return 0
}

function stop()
{
    echo > "${STOP_FILE}"

    while (( 1 == 1 ))
    do
      local c=$(ps -lef | grep "${PYTHON_FILE}" | grep -v 'grep' | wc -l)
      if [ ${c} -gt 0 ]; then
        echo "Please waiting..."
        sleep 1
      else
        echo "Stop OK!!!"
        break
      fi
    done

    return 0
}

function restart()
{
    stop
    if [ 0 -ne $? ];then
        return 1
    fi

    start
    return $?
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
