#!/bin/sh
#
# openvas-scanner    This starts and stops the OpenVAS scanner.
#
# chkconfig:   35 75 25
# description: This starts and stops the OpenVAS scanner.
# processname: /usr/sbin/openvassd
# config:      /etc/openvas/openvassd.conf
# pidfile:     /var/run/openvassd.pid
#
### BEGIN INIT INFO
# Provides: $openvas-scanner
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

EXEC="/usr/sbin/openvassd"
PROG=$(basename $EXEC)

# Check for missing binaries (stale symlinks should not happen)
# Note: Special treatment of stop for LSB conformance
test -x $EXEC || { echo "$EXEC not installed"; 
	if [ "$1" = "stop" ]; then exit 0;
	else exit 5; fi; }

# Check for existence of needed config file
OPENVASSD_CONFIG=/etc/sysconfig/openvas-scanner
test -r $OPENVASSD_CONFIG || { echo "$OPENVASSD_CONFIG does not exist";
	if [ "$1" = "stop" ]; then exit 0;
	else exit 6; fi; }

# Read config	
. $OPENVASSD_CONFIG

# Build parameters
[ "$SCANNER_ADDRESS" ] && PARAMS="$PARAMS --listen=$SCANNER_ADDRESS"
[ "$SCANNER_PORT" ]    && PARAMS="$PARAMS --port=$SCANNER_PORT"

LOCKFILE=/var/lock/subsys/$PROG

start() {
    echo -n $"Starting openvas-scanner: "
    daemon $EXEC $PARAMS
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && touch $LOCKFILE
    return $RETVAL
}

stop() {
    echo -n $"Stopping openvas-scanner: "
    killproc $PROG
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && rm -f $LOCKFILE
    return $RETVAL
}

restart() {
    stop
    start
}

reload() {
    echo -n $"Reloading openvas-scanner: "
    killproc $PROG -HUP
    RETVAL=$?
    echo
    return $RETVAL
}

force_reload() {
    restart
}

fdr_status() {
    status $PROG
}

case "$1" in
    start|stop|restart|reload)
        $1
        ;;
    force-reload)
        force_reload
        ;;
    status)
        fdr_status
        ;;
    condrestart|try-restart)
        [ ! -f $LOCKFILE ] || restart
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|try-restart|reload|force-reload}"
        exit 2
esac

