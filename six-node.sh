gnome-terminal --title "Router 1" --window -e "bash -c \"python3 src ./configs/networks/six-node/01.conf; exec bash\"" &
gnome-terminal --title "Router 2" --window -e "bash -c \"python3 src ./configs/networks/six-node/02.conf; exec bash\"" &
gnome-terminal --title "Router 3" --window -e "bash -c \"python3 src ./configs/networks/six-node/03.conf; exec bash\"" &
gnome-terminal --title "Router 4" --window -e "bash -c \"python3 src ./configs/networks/six-node/04.conf; exec bash\"" &
gnome-terminal --title "Router 5" --window -e "bash -c \"python3 src ./configs/networks/six-node/05.conf; exec bash\"" &
gnome-terminal --title "Router 6" --window -e "bash -c \"python3 src ./configs/networks/six-node/06.conf; exec bash\""