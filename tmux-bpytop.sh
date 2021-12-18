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
        tmux new-session -d -s "$SESS" "btop ; tmux kill-session -t $SESS" \;\
             split-window -t "$SESS.1" -h -l 74 '
            while true; do
                clear
                curl -s "v2.wttr.in?lang=de&F" | head -n-3
                curl -s "wttr.in/moon?F"
                sleep 1h
            done'
        tmux new-window -t "$SESS" "cd $HOME/Workspace/uucharmap ; while true; do ./txtout.py | less -R; done" \;\
             split-window -t "$SESS:2" -h -l 80 "colorterm keen" \;\
             select-pane -t "$SESS.1" \;\
             rename-window -t "$SESS" "🌈" \;\
             select-window -t "$SESS:1" \;\
             select-pane -t "$SESS.1" \;\
             rename-window -t "$SESS" "💻"
         
        tmux set-window-option -t "$SESS:2" monitor-activity off \;\
             set-window-option -t "$SESS:1" monitor-activity off \;\
             set-option -t "$SESS:1" window-active-style none \;\
             set-option -t "$SESS:2" window-active-style none
        
        tmux set-hook -t "$SESS" after-new-window 'if -F "#{==:#{session_name},'$SESS'}" "set-option window-active-style none" ""' \;\
             set-option -t "$SESS" status-style "none,fg=yellow" \;\
             set-option -t "$SESS" pane-border-style "fg=color237" \;\
             set-option -t "$SESS" pane-active-border-style "fg=color237"

        echo "Session $SESS created".
    fi

    # resizing pane again after attach is neccessary.
    (   sleep 0.4
        tmux resize-pane -t "$SESS:1.2" -x 74 
        tmux select-window -t "$SESS:2"
        tmux resize-pane -t "$SESS:2.2" -x 80
        tmux select-window -t "$SESS:1"
    ) &
    
    tmux attach -t "$SESS"
    slack
done
