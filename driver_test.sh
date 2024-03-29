#usage: ./driver_test.sh unique_str_for_zookeeper_docker_id port1 port2 port3
#ports must be different, available ports
echo "killing old dockers in case they didnt shut down correctly, and also old python servers"
sleep 2
./kill_dockers.sh
killall python3

echo "Running all three tests..."

echo "Starting Zookeeper Docker in BG"
sleep 5
./zk.sh $1

echo "Starting 3 servers in BG and listening on the specified ports"
sleep 2
nohup ./start_server.sh $2 &
S1_PID=$! #i am the leader node until test2
LEADER_P=$2
nohup ./start_server.sh $3 &
S2_PID=$!
nohup ./start_server.sh $4 &
S3_PID=$!

sleep 60

echo "Running test one"
python3 -u run_test1_requests.py $2 $3 $4
sleep 3

echo "Killing Leader Node..."
kill $S1_PID
echo "Because zookeeper takes 30 seconds to remove ephermeal nodes, we must wait 30 seconds"
sleep 35

echo "Running test two"
python3 -u run_test2_requests.py $3 $4

NEW_LEADER_P=$((LEADER_P+1))
echo "Bringing old leader back up"
nohup ./start_server.sh $NEW_LEADER_P &
S1_PID=$!
sleep 3

echo "Runnign requests for test 3"
python3 -u run_test3_requests.py $NEW_LEADER_P $3 $4

kill $S1_PID
kill $S2_PID
kill $S3_PID
./kill_dockers.sh
killall python3
