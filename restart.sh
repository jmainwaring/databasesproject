# Stop containers that are running and delete them
docker stop web mysql-server
docker system prune -af
bash startup.sh
