#!/bin/bash

SESS="KeenTerm"

slack() {
    # a bit of fancy slack, to allow Ctrl-C. looks better than "sleep 2" :)
    PROG=(
        "Fondling snugglewoofs..."
        "Quadrizing circulars..."
        "Validating p=np..."
        "Counting to infinity twice..."
        "Almost done..."
        "Launch!"
    )
    echo -e "\n\e[97mRespawning...  \e[33m Press Ctrl-C to abort!\e[0m"
    for i in $(seq ${#PROG[@]}); do
        printf "\r[\r\e[${i}C=\r\e[$((${#PROG[@]}+1))C] ${PROG[(i-1)]}\e[K"
        sleep .3
    done
    echo
}

sleep .2 # wait for vte to realize :/

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
        echo "Session $SESS created".
    fi

    # resizing pane again after attach may be neccessary.
    (sleep .3 ; tmux resize-pane -t "$SESS:1.2" -x 74) &
    tmux attach -t "$SESS"
    slack
done
