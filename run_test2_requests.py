import requests
import sys

s2_port = sys.argv[1]
s3_port = sys.argv[2]

node_ip = "127.0.0.1"

node_data = node_ip + ":" + s2_port
the_key = "key0"
the_val = "val1"

#now that we have new leader, we will set a new value
print("setting key0=val1 now that leader is dead and there is a new one")
r = requests.get("http://"+node_data+"/"+the_key+"/"+the_val)
r = r.content.decode()
print("getting value for key0 from that node")
r = requests.get("http://"+node_data+"/"+the_key)
r = r.content.decode()
print(f"req for key0 should be val1: {r}")

#get key0 from a different node to make sure it propogated from new leader
node_data = node_ip + ":" + s3_port
print("getting value of key0 on a differnt node")
r = requests.get("http://"+node_data+"/"+the_key)
r = r.content.decode()
print(f"req for key0 from diff node should be val1: {r}")
