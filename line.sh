gnome-terminal --title "Router 1" --window -e "bash -c \"python3 src ./configs/networks/line/1.conf; exec bash\"" &
gnome-terminal --title "Router 2" --window -e "bash -c \"python3 src ./configs/networks/line/2.conf; exec bash\"" &
gnome-terminal --title "Router 3" --window -e "bash -c \"python3 src ./configs/networks/line/3.conf; exec bash\""