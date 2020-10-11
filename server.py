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
zkport = sys.argv[7]

logging.basicConfig()

#setup for zookeeper

zk = KazooClient(hosts=zkip+':'+zkport)
zk.start()


#make sure election file exists
try:
    zk.create("/election/")
except:#just skip if already exists
    pass


#create node for this server
#data is ip:port of the server
zk.create("/election/", bytes(host_ip+":"+host_port, encoding='ascii'), ephemeral=True ,sequence=True)

def leader_func():
    this_node_is_leader = True
    print("LOOK AT ME, I'M THE CAPTAIN NOW")
    return


#do new leader election
election = zk.Election("/election")
ret_val = election.run(leader_func)

#set up watch
@zk.DataWatch('/election')
def contend_for_leader(data,val):
    print("Contending for leader")
    this_node_is_leader = False
    election = zk.Election("/election")
    ret_val = election.run(leader_func)
    print(f"ret_val: {ret_val}") #TODO look at this

class ReadValue(Resource):
    def get(self, the_key):
        if the_key in the_dict:
            return the_dict[the_key]
        else:
            return None


def set_new_value_globally(the_key, the_value):
    the_nodes = kz.get_children("/election")
    for n in the_nodes:
        node_data = zk.get("/election/"+n)[0].decode()
        r = requests.get(the_leader_data+"/FromLeader/"+the_key+"/"the_val)

def send_new_value_to_leader(the_key, the_val):
    the_nodes = kz.get_children("/election")
    leader_num = sorted(children)[0]
    the_leader_data = zk.get("/election/"+leader_num)[0].decode()
    r = requests.get(the_leader_data+"/ForLeader"+the_key+"/"the_val)

class AddUpdateValue(Resource):
    def get(self, the_key, the_val):
        send_new_value_to_leader(the_key, the_val)
        

class AUVForLeader(Resource):
    def get(self, the_key, the_val):
        set_new_value_globally(the_key, the_val)
        

class AUVFromLeader(Resource):
    def get(self, the_key, the_val):
        the_dict[the_key] = the_val



api.add_resource(ReadValue, '/<string:the_key>')
api.add_resource(AddUpdateValue, '/<string:the_key>/<string:the_val>')
api.add_resource(AUVForLeader, '/ForLeader/<string:the_key>/<string:the_val>')
api.add_resource(AUVFromLeader, '/FromLeader/<string:the_key>/<string:the_val>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(host_port))

