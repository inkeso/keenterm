#!/bin/bash

SESS="KeenTerm"

TOPTOOL="btop"
#TOPTOOL="htop"
#TOPTOOL="top"

# endless loop, to keep terminal running
while true; do
    if ! tmux has-session -t "$SESS" 2>/dev/null ; then
        tmux new-session -d -s "$SESS" "$TOPTOOL ; tmux kill-session -t $SESS" \;\
             rename-window -t "$SESS" "💻" \;\
             set-window-option -t "$SESS:1" monitor-activity off
    fi
    tmux attach -t "$SESS"
    echo "Detached/Terminated. Hit Enter to restart, Ctrl-C to quit."
    read
done
