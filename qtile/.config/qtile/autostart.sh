#!/bin/bash
setxkbmap -layout us,ru -option grp:win_space_toggle
picom --config $HOME/.config/picom/picom.conf &

# Blur lock on idle / suspend (xss-lock delays suspend until the lock is up).
xset s 300 300
xss-lock --transfer-sleep-lock -- "$HOME/.local/bin/blur-lock" &
