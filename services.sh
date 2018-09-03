#bin/bash

autoadmin_dir='./'
PROC_NAME="autoadmin"
lockfile=/var/lock/subsys/${PROC_NAME}

start() {
        if [ $(whoami) != 'root' ];then
            echo "Sorry, AutoAdmin must be run as root"
            exit 1
        fi

        nohup python $autoadmin_dir/manage.py runserver 0.0.0.0:8000 & > /dev/null
        if [ $? == 0 ];then
        	echo success "autoadmin_start"

        nohup python $autoadmin_dir/manage.py runserver 0.0.0.0:8000 &> /dev/null
        if [ $? == 0 ];then
            if [ ! -e $lockfile ]; then
                lockfile_dir=`dirname $lockfile`
                mkdir -pv $lockfile_dir
            fi
            touch "$lockfile"
        else
            echo "$autoadmin_start"

        fi

}


stop() {
    echo -n $"Stopping ${PROC_NAME} service:"
    ps aux | grep -E 'runserver' | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ]; then
        echo_success
        rm -f "$lockfile"
    else
        echo
        rm -f "$lockfile"
    fi

}

status(){
    ps axu | grep 'run_server' | grep -v 'grep' &> /dev/null
    if [ $? == '0' ];then
        echo -n "cloud_monitor/autoadmin is running..."
        touch "$lockfile"
    else
        echo -n "cloud_monitor/autoadmin is not running."
    fi
}



restart(){
    stop
    start
}

case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;

  restart)
        restart
        ;;

  status)
        status
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
