#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$SCRIPT_DIR/database/report"
PID_FILE="$SCRIPT_DIR/.server.pid"
CRON_TAG="# webserver-manage"

mkdir -p "$REPORT_DIR"

usage() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Cron jobs:"
    echo "  cron:start    Create cron jobs (Mon-Thu 6pm run.sh, Fri 6pm run.sh weekly)"
    echo "  cron:stop     Remove cron jobs"
    echo "  cron:status   Show cron job status"
    echo ""
    echo "Web server:"
    echo "  server:start   Start the web server"
    echo "  server:stop    Stop the web server"
    echo "  server:restart Restart the web server"
    echo "  server:status  Show web server status"
}

cron_start() {
    TASK_WEEKDAY="/home/cyu3/projects/minifincode/run.sh"
    TASK_FRIDAY="/home/cyu3/projects/minifincode/run.sh weekly"
    LOG_WEEKDAY="$REPORT_DIR/cron_weekday.log"
    LOG_FRIDAY="$REPORT_DIR/cron_friday.log"

    TASK_WEEKDAY_CRON="0 18 * * 1-4 $TASK_WEEKDAY >> $LOG_WEEKDAY 2>&1 $CRON_TAG"
    TASK_FRIDAY_CRON="0 18 * * 5 $TASK_FRIDAY >> $LOG_FRIDAY 2>&1 $CRON_TAG"

    (crontab -l 2>/dev/null | grep -v "$CRON_TAG"; echo "$TASK_WEEKDAY_CRON"; echo "$TASK_FRIDAY_CRON") | crontab -

    echo "Cron jobs created (Mon-Thu 6pm, Fri 6pm weekly). Logs go to $REPORT_DIR"
}

cron_stop() {
    crontab -l 2>/dev/null | grep -v "$CRON_TAG" | crontab -
    echo "Cron jobs removed."
}

cron_status() {
    ENTRIES=$(crontab -l 2>/dev/null | grep "$CRON_TAG" || true)
    if [ -z "$ENTRIES" ]; then
        echo "Status: stopped"
    else
        echo "Status: running"
        echo "$ENTRIES"
    fi
}

server_start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Server already running (PID $(cat "$PID_FILE"))"
        exit 1
    fi
    cd "$SCRIPT_DIR"
    nohup /home/cyu3/pyenv/bin/python "$SCRIPT_DIR/app.py" \
        >> "$REPORT_DIR/server.log" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Server started (PID $(cat "$PID_FILE"))"
}

server_stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Server may not be running."
        pkill -f "python.*app.py" 2>/dev/null && echo "Killed stray processes." || true
        return
    fi
    PID=$(cat "$PID_FILE")
    if kill "$PID" 2>/dev/null; then
        echo "Server stopped (PID $PID)"
    else
        echo "Process $PID not found."
    fi
    rm -f "$PID_FILE"
    pkill -f "python.*app.py" 2>/dev/null || true
}

server_restart() {
    server_stop
    sleep 1
    server_start
}

server_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        PID=$(cat "$PID_FILE")
        UPTIME=$(ps -o etime= -p "$PID" 2>/dev/null | xargs)
        echo "Status: running"
        echo "PID:    $PID"
        echo "Uptime: $UPTIME"
    elif pgrep -f "python.*app.py" >/dev/null 2>&1; then
        echo "Status: running (no PID file, PID $(pgrep -f "python.*app.py" | head -1))"
    else
        echo "Status: stopped"
    fi
}

case "${1:-help}" in
    cron:start)   cron_start ;;
    cron:stop)    cron_stop ;;
    cron:status)  cron_status ;;
    server:start)  server_start ;;
    server:stop)   server_stop ;;
    server:restart) server_restart ;;
    server:status)  server_status ;;
    help|--help|-h) usage ;;
    *) echo "Unknown command: $1"; usage; exit 1 ;;
esac
