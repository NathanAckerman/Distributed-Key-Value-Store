import sys
import requests
from flask import *
from flask_restful import Resource, Api
from kazoo.client import KazooClient
import logging

#setup for flask
app = Flask(__name__)
api = Api(app)
the_dict = {}
this_node_is_leader = False

#python server.py –host <hostip> –port <xxxx> -zookeeper <zkip> -zookeeper_port
#<zkport>

host_ip = sys.argv[2]
host_port = sys.argv[4]
zkip = sys.argv[6]
zkport = sys.argv[8]

logging.basicConfig()

#setup for zookeeper

zk = KazooClient(hosts=str(zkip)+':'+str(zkport))
zk.start()


#make sure election file exists
try:
    zk.create("/election/")
except:#just skip if already exists
    pass


#create node for this server
#data is ip:port of the server
zk.create("/election/", bytes(host_ip+":"+host_port, encoding='ascii'), ephemeral=True ,sequence=True)

#set up watch
@zk.ChildrenWatch('/election')
def contend_for_leader(children):
    print("Contending for leader")
    this_node_is_leader = False
    the_nodes = children
    print("nodes in sys to find leader:")
    print(the_nodes)
    leader_num = sorted(the_nodes)[0]
    the_leader_data = zk.get("/election/"+leader_num)[0].decode()
    if host_ip in the_leader_data and host_port in the_leader_data:
        print("i am the leader")
        this_node_is_leader = True
    else:
        print("i am not the leader")

class ReadValue(Resource):
    def get(self, the_key):
        if the_key in the_dict:
            return the_dict[the_key]
        else:
            return None


def set_new_value_globally(the_key, the_val):
    the_nodes = zk.get_children("/election")
    print("nodes in system:")
    print(the_nodes)
    for n in the_nodes:
        node_data = zk.get("/election/"+n)[0].decode()
        print(node_data)
        try:
            r = requests.get("http://"+node_data+"/FromLeader/"+the_key+"/"+the_val, timeout=5)
            print("not passing")
        except:
            print("passing")
            pass

def send_new_value_to_leader(the_key, the_val):
    print("sending new value to leader")
    the_nodes = zk.get_children("/election")
    print("nodes in sys to find leader:")
    print(the_nodes)
    leader_num = sorted(the_nodes)[0]
    the_leader_data = zk.get("/election/"+leader_num)[0].decode()
    r = requests.get("http://"+the_leader_data+"/ForLeader/"+the_key+"/"+the_val)
    print("done with leader")

class AddUpdateValue(Resource):
    def get(self, the_key, the_val):
        print("update req received")
        send_new_value_to_leader(the_key, the_val)
        return the_key + " = " + the_val
        

class AUVForLeader(Resource):
    def get(self, the_key, the_val):
        set_new_value_globally(the_key, the_val)
        return "done"
        

class AUVFromLeader(Resource):
    def get(self, the_key, the_val):
        the_dict[the_key] = the_val
        return "done"



api.add_resource(ReadValue, '/<string:the_key>')
api.add_resource(AddUpdateValue, '/<string:the_key>/<string:the_val>')
api.add_resource(AUVForLeader, '/ForLeader/<string:the_key>/<string:the_val>')
api.add_resource(AUVFromLeader, '/FromLeader/<string:the_key>/<string:the_val>')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=int(host_port))

