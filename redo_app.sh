docker stop web
docker container rm web
docker build -t webserver .
docker run --network sql-network --name web -d -e FLASK_APP=webapp.py -p 5000:5000 webserver
