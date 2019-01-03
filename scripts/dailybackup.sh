#!/bin/bash

# Call this in your root's crontab to run once a day on weekdays
# Example call: /path/to/scotuswebcites/scripts/dailybackup.sh /path/to/backup/directory

function getSetting {
    if [[ -f "$SETTINGS_FILE" ]]; then
        grep "'$1':" "$SETTINGS_FILE" | awk '{print $2}' | sed "s/',$//g" | sed "s/'$//g" | sed "s/^'//g"
    fi
}

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root"
    exit 1
fi

CONFIG="/root/.my.cnf"
if [ ! -f "$CONFIG" ]; then
    echo
    echo "Please create $CONFIG with 600 permissions and add the following lines:"
    echo
    echo "[mysql]"
    echo "user=scotuswebcites"
    echo "password=<YOU-PASSWORD-FROM-settings.py>"
    echo
    echo "[mysqldump]"
    echo "user=scotuswebcites"
    echo "password=<YOU-PASSWORD-FROM-settings.py>"
    echo
    exit 1
fi

if [[ "$#" -ne 1 ]]; then
    echo "Usage: ./dailybackup.sh /path/to/backup/dir"
    exit 1
fi

# User and password should be set in /root/.my.cnf
DAY=$(date +%A)
BACKUP_DIR="$1"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SETTINGS_FILE="$SCRIPT_DIR"/../scotuswebcites/settings.py
DATABASE_NAME=$(getSetting 'NAME')
DATABASE_HOST=$(getSetting 'HOST')
DATABASE_PORT=$(getSetting 'PORT')

if [[ -n "$DATABASE_HOST" && -n "$DATABASE_PORT" && -n "$DATABASE_NAME" ]]; then

    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir "$BACKUP_DIR"
    fi

    OUTPUT="$BACKUP_DIR/$DAY.sql.gz"
    mysqldump -h "$DATABASE_HOST" -P "$DATABASE_PORT" "$DATABASE_NAME" | gzip -c | cat > "$OUTPUT"
    chmod 600 "$OUTPUT"
else
    echo "ERROR: Could not establish database variables from settings.py file."
fi
