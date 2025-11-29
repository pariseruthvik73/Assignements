#! /bin/bash


Code_to_monitor=500
who_to_inform="livingdevops@gmail.com"

# $0 -> filename
# $1 -> first argument, $2 -> second argument
# $# -> number of arguments passed

# take arguments -> allow people to pass the log file as an argument
LOGFILE=$1


# make sure that i pass a file name by watching argument count
if  [ $# -ne 1 ]; then
    echo "Usage: $0 <logfile>"
    exit 1
fi

# make sure my filename is correct
if [ ! -f "$LOGFILE" ]; then
    echo "Error: File '$LOGFILE' not found!"
    exit 1
fi

echo "Monitoring log file: $LOGFILE"


# monitor the log file for 500 response codes
tail -f "$LOGFILE" | while read LINE; do

    # extract the response code from the line
    # RESPONSE_CODE=$(echo "$LINE" | awk '{print $9}')

    rc=$(echo "$LINE" | awk -F '"' '{print $3 }' | awk '{print $1}') # run the cli on subshell

    # or rc = ` echo "$LINE" |awk -F '"' '{print $3 }' | awk '{print $1}'`
    
    endpoint=$(echo "$LINE"  | awk  '{print $7 }' )  

    # echo "Response code: $rc for endpoint: $endpoint"   
    # check if the response code matches the code to monitor

    if [ $rc -eq $Code_to_monitor ]; then
        # send an alert (for simplicity, we'll just echo a message)
        echo "ALERT: Detected $Code_to_monitor response code for endpoint $endpoint"
        # In real scenario, you might use mail command to send email
        # echo "ALERT: Detected $Code_to_monitor response code" | mail -s "Alert: $Code_to_monitor Response Code Detected" $who_to_inform
    fi
    done



