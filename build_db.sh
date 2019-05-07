pushd db
docker network create my-network
docker run -d --name mysql-server --network my-network -e MYSQL_ROOT_PASSWORD=secret mysql --default-authentication-plugin=mysql_native_password
popd

cat initialize.sql | docker exec -i mysql-server mysql -uroot --password=secret