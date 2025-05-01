import argparse
import os
import pickle
#change all address
# python3 ProtocolInitiator_DeployContracts.py --params-address 0xCdf08c88CB97E29AaC333f5580268e209b9AF08F --request-address 0x583a474d6510baBd30ac81956faa3874eB980322 --issue-address 0xD44B28a43A618b82367dD386C7A66c2791c5d4b7 --opening-address 0xdAF312EFb4d5cbf64c61C46e258C79c8F0DFa332


parser = argparse.ArgumentParser(description="Smart Contracts Deployment")
# parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which Protocol Initiator is running.")
parser.add_argument("--params-address", type=str, default = None, required = True,  help= "The blockchain address at which params contract is deployed.")
parser.add_argument("--request-address", type=str, default = None, required = True,  help= "The blockchain address at which request contract is deployed.")
parser.add_argument("--issue-address", type=str, default = None, required = True,  help= "The blockchain address at which issue contract is deployed.")
parser.add_argument("--opening-address", type=str, default = None, required = True,  help= "The blockchain address at which opening contract is deployed.")
# parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a client is connected to blockchain network.")
args = parser.parse_args()

mode = 0o777
root_dir = os.path.join(os.getcwd(), "ROOT")
try:
	os.mkdir(root_dir, mode = mode)
except FileExistsError as e:
	pass

def uploadAddresses(address, filename):
	file_path = os.path.join(root_dir, filename)
	f = open(file_path,'wb')
	pickle.dump(address, f)
	f.close()

#print(args.params_address)
#print("Displaying Output as: % s" % args.params_address)
uploadAddresses(args.params_address, "params_address.pickle")
uploadAddresses(args.request_address, "request_address.pickle")
uploadAddresses(args.issue_address, "issue_address.pickle")
uploadAddresses(args.opening_address, "opening_address.pickle")