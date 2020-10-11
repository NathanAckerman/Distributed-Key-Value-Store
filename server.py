import sys
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
#if zk.exists("/election/") is None:
#    zk.create("/election/")

try:
    zk.create("/election/")
except:
    pass

#does_exist = zk.exists("/election/")
#print(f"exists: {does_exist}")

zk.create("/election/", bytes(host_ip+":"+host_port, encoding='ascii'), ephemeral=True ,sequence=True)
children = zk.get_children("/election/")


def leader_func():
    this_node_is_leader = True
    print("LOOK AT ME, I'M THE CAPTAIN NOW")
    return



#do new leader election
election = zk.Election("/election")
ret_val = election.run(leader_func)
print(f"ret_val: {ret_val}") #TODO look at this

#set up watch
@zk.ChildrenWatch('/election')
def contend_for_leader(children):
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
    return "TODO"

def send_new_value_to_leader(the_key, the_val):
    return "TODO"

class AddUpdateValue(Resource):
    def get(self, the_key, the_val):
        return send_new_value_to_leader(the_key, the_val)
        

class AUVForLeader(Resource):
    def get(self, the_key, the_val):
        return set_new_value_globally(the_key, the_val)
        

class AUVFromLeader(Resource):
    def get(self, the_key, the_val):
        the_dict[the_key] = the_val



api.add_resource(ReadValue, '/<string:the_key>')
api.add_resource(AddUpdateValue, '/<string:the_key>/<string:the_val>')
api.add_resource(AUVForLeader, '/<string:the_key>/<string:the_val>')
api.add_resource(AUVFromLeader, '/<string:the_key>/<string:the_val>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(host_port))

