docker run --name $1 --restart always -d zookeeper
docker run -it --rm --link $1:zookeeper zookeeper zkCli.sh -server zookeeper
