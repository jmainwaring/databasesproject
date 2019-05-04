# startup.sh: script to create docker containers

# Create network
docker network create sql-network


# Run SQL container
docker run -d --name mysql-server --network sql-network -e MYSQL_ROOT_PASSWORD=secret mysql --default-authentication-plugin=mysql_native_password

# Run initializing script out of Python
pushd init
docker build -t init_img .
docker run --network sql-network --name init -d -e FLASK_APP=init_db.py -p 5000:5000 init_img
docker stop init
docker container rm init
popd

# Build and create container with web app
docker build -t webserver .
docker run --network sql-network --name web -d -e FLASK_APP=webapp.py -p 5000:5000 webserver