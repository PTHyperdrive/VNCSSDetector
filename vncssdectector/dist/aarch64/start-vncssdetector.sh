#!/system/bin/sh
# VNCSSdetector start/stop script for Android
# Run with: su -c '/data/vncssdetector/start-vncssdetector.sh start'

DAEMON=/data/vncssdetector/vncssdetector-daemon
CONFIG=/data/vncssdetector/config.toml
PIDFILE=/data/vncssdetector/vncssdetector.pid
LOGFILE=/data/vncssdetector/vncssdetector.log

case "$1" in
    start)
        echo "Starting VNCSSdetector..."
        
        # Check if already running
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "VNCSSdetector already running (PID: $PID)"
                exit 0
            fi
        fi
        
        # Set permissions for /dev/diag if needed
        if [ -e /dev/diag ]; then
            chmod 666 /dev/diag 2>/dev/null || true
        fi
        
        # Start the daemon
        export RUST_LOG=info
        nohup $DAEMON $CONFIG > $LOGFILE 2>&1 &
        echo $! > $PIDFILE
        
        sleep 1
        if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
            echo "VNCSSdetector started (PID: $(cat $PIDFILE))"
            echo "Web interface: http://localhost:8080"
        else
            echo "Failed to start VNCSSdetector. Check log: $LOGFILE"
            cat $LOGFILE
            exit 1
        fi
        ;;
        
    stop)
        echo "Stopping VNCSSdetector..."
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$PIDFILE"
                echo "VNCSSdetector stopped"
            else
                echo "VNCSSdetector not running"
                rm -f "$PIDFILE"
            fi
        else
            echo "VNCSSdetector not running (no PID file)"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
        
    status)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "VNCSSdetector is running (PID: $PID)"
                exit 0
            fi
        fi
        echo "VNCSSdetector is not running"
        exit 1
        ;;
        
    log)
        if [ -f "$LOGFILE" ]; then
            cat "$LOGFILE"
        else
            echo "No log file found"
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|log}"
        exit 1
        ;;
esac

exit 0
