#!/bin/bash 
# csh, zsh, sh

who_to_inform="livingdevops@gmail.com"
LOGFILE=$1
code_to_monitor=500

if [ $# -eq 0 ]; then
    # $0 = script name, display usage message
    echo "Usage: $0 <log_file_path>"
    exit 1  # Exit with error code 1
fi

if_file_exists(){
    if [ ! -f "$LOGFILE" ]; then
        echo "Error: File $LOGFILE not found!"
        exit 1
    fi
}


# create a function that take log fil as input and monitor 500 response code
monitor_log_file() {
    initial_size=$(stat -c%s "$LOGFILE" 2>/dev/null || echo 0)
    tail -F -c +$((initial_size + 1)) "$LOGFILE" | while read -r LINE; do
        rc=$(echo "$LINE" | awk -F '"' '{print $3 }' | awk '{print $1}')
        echo "Response code: $rc"
        endpoint=$(echo "$LINE"  | awk  '{print $7 }' )  
        
        if [ "$rc" -eq "$code_to_monitor" ]; 
        then
            echo -e "Hey $who_to_inform\nALERT: Detected $rc response code for endpoint $endpoint"
        fi
    done
}




# check if file exists
if_file_exists

# monitor the log file
monitor_log_file



#### fixed script below ####