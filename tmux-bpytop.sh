#!/bin/bash

SESS="KeenComm"

# endless loop, to keep terminal running
while true; do
    if ! tmux has-session -t "$SESS" 2>/dev/null ; then
        tmux new-session -d -s "$SESS" "sleep .2; bpytop"
        tmux rename-window -t "$SESS" "💻"
        tmux set-hook -t "$SESS" after-new-window 'if -F "#{==:#{session_name},'$SESS'}" "set-option window-active-style none" ""'
        tmux set-option -t "$SESS" window-active-style none
        tmux set-option -t "$SESS" status-style "none,fg=yellow"
    fi
    tmux attach -t "$SESS"
    
    # a bit of slack, to allow Ctrl-C
    sleep .1 ; echo "tmux is kill. Respawning..."
    sleep .3 ; echo "Fondling snugglewoofs..."
    sleep .3 ; echo "Quadrizing circulars..."
    sleep .3 ; echo "Validating p=np..."
    sleep .3 ; echo "Counting to infinity twice..."
    sleep .3 ; echo "Almost done..."
    sleep .3 ; echo "Launch!"
done
