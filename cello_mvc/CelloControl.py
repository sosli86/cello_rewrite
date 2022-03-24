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

    # setters

    def set_web3(self, web3: Web3):
        self.web3 = web3
    
    def set_model(self, model: UserMod):
        self.model = model
    
    def set_username(self, username):
        self.user_name = username
    
    # keygens    
    # contract functions
    
    def open_contract(self, contract_name, contract_address=""):
        if contract_address == "":
            self.model.contracts[contract_name] = ActiveContract(self.web3, contract_name)
            self.model.contract_membership_authenticated.append(contract_name)
            contract_address = self.model.contracts[contract_name].contract_address
            print("Contract created.")
        else:
            self.model.contracts[contract_name] = ActiveContract(self.web3, contract_name, contract_address)
            print("Contract instantiated.")
    
    def add_new_message(self, contract_name, new_message):
        self.model.add_message_to_contract(contract_name, new_message)
    
    def add_new_pub_key(self, contract_name, user_name, new_pub_key):
        self.model.add_pub_key_to_contract(contract_name, user_name, new_pub_key)
    
    # loop functions

    def update_messages(self):
        for contract in self.model.contract_membership_authenticated:
            self.model.update_messages_from_contract(contract)
            self.model.write_message_logs_to_database(contract)
        self.model.populate_message_archives_from_database()
    
    def update_pubkeys(self):
        for contract in self.model.contract_membership_authenticated:
            self.model.update_pub_keys_from_contract(contract)
    
    def update_keyciphers(self):
        for contract in self.model.contract_membership_authenticated:
            self.model.update_key_ciphers_from_contract(contract)