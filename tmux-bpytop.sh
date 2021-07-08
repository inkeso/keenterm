#!/bin/bash

SESS="KeenComm"

# wait a bit until terminal is realized
sleep .1

# endless loop, to keep terminal running
while true; do
    if ! tmux has-session -t "$SESS" 2>/dev/null ; then
        tmux new-session -d -s "$SESS" "bpytop ; tmux kill-pane -t $SESS.2"
        tmux split-window -t "$SESS.1" -h -l 74 '
            while true; do
                clear
                curl -s "v2.wttr.in?lang=de&F" | head -n-3
                curl -s "wttr.in/moon?F"
                sleep 1h
            done'
        tmux select-pane -t "$SESS.1"
        tmux rename-window -t "$SESS" "💻"
        tmux set-hook -t "$SESS" after-new-window 'if -F "#{==:#{session_name},'$SESS'}" "set-option window-active-style none" ""'
        tmux set-option -t "$SESS" window-active-style none
        tmux set-option -t "$SESS" status-style "none,fg=yellow"
        tmux set-option -t "$SESS" pane-border-style "fg=color237"
        tmux set-option -t "$SESS" pane-active-border-style "fg=color237"
    fi
    tmux attach -t "$SESS"
    
    # a bit of slack, to allow Ctrl-C

    sleep .1 ; echo "tmux is kill. Respawning...        Press Ctrl-C to abort!"
    sleep .3 ; echo "Fondling snugglewoofs..."
    sleep .3 ; echo "Quadrizing circulars..."
    sleep .3 ; echo "Validating p=np..."
    sleep .3 ; echo "Counting to infinity twice..."
    sleep .3 ; echo "Almost done..."
    sleep .3 ; echo "Launch!"
done
