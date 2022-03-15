from cello_mvc.CelloMod import UserMod, ActiveContract
from web3.providers.eth_tester import EthereumTesterProvider
from web3 import Web3
from eth_tester import PyEVMBackend
from threading import *
import time
import string
import secrets

def get_web3(rpc=None):
    if not rpc:
        return Web3(EthereumTesterProvider(PyEVMBackend()))
    else:
        return Web3(rpc=rpc)

class CelloControl:
    
    def set_model(self, model):
        self.model = model
    
    def contract_key_gen(self, contract_name):
        contract_key = print(''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7)))
        print(contract_key)
        self.model.contract_keys[contract_name] = contract_key
        return contract_key
    
    def encrypt_contract_key(self, contract_key):
        return str(self.model.gpg.encrypt(contract_key, self.user_name))
    
    def add_new_contract(self, contract_name, contract_key = "", contract_address=""):
        if contract_address == "":
            self.model.contracts[contract_name] = ActiveContract(self.web3, contract_name)
            contract_address = self.model.contracts[contract_name].contract_address
            print("Contract created.")

            if contract_key == "":
                contract_key = self.contract_key_gen(contract_name)

            contract_key_cipher = self.encrypt_contract_key(contract_key)

            self.model.add_key_cipher_to_contract(contract_name, contract_key_cipher)
            self.model.add_pub_key_to_contract(contract_name, str(self.model.gpg.export_keys(self.user_name)))
            self.model.add_message_to_contract(contract_name, f'Welcome to { contract_name }!')

        else:
            self.model.contracts[contract_name] = ActiveContract(self.web3, contract_name, contract_address)
    
    def add_new_message(self, contract_name, new_message):
        self.model.add_message_to_contract(contract_name, new_message)
    
    def add_new_pub_key(self, contract_name, new_pub_key):
        self.model.add_pub_key_to_contract(contract_name, new_pub_key)

    def __init__(self, web3: Web3, model: UserMod, user_name):

        self.default_address = web3.eth.default_account

        self.web3 = web3

        self.user_name = user_name
        
        self.model = model