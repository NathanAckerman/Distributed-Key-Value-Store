import requests
import sys

s1_port = sys.argv[1]
s2_port = sys.argv[2]
s3_port = sys.argv[3]

node_ip = "127.0.0.1"

node_data = node_ip + ":" + s1_port
the_key = "key0"
the_val = "val2"
r = requests.get("http://"+node_data+"/"+the_key)
r = r.content.decode()
print(f"req for key0 on old leader should be stale and should be nothing: {r}")

node_data = node_ip + ":" + s2_port
print("setting key0=val2 from another node")
r = requests.get("http://"+node_data+"/"+the_key+"/"+the_val)
r = r.content.decode()

print("getting value for key0 from old leader")
node_data = node_ip + ":" + s1_port
r = requests.get("http://"+node_data+"/"+the_key)
r = r.content.decode()
print(f"req for key0 from old leader should be val2: {r}")

