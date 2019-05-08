# Creating network
docker network create my-network


# Building SQL container
docker run -d --name mysql-server --network my-network -e MYSQL_ROOT_PASSWORD=secret mysql --default-authentication-plugin=mysql_native_password
sleep 12


# Build and create container with web app
docker build -t webserver .
docker run --network my-network --name web -d -e FLASK_APP=webapp.py -p 5000:5000 webserver


cat initialize.sql | docker exec -i mysql-server mysql -uroot --password=secret
