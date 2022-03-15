import time
import threading

from solcx import compile_source
from web3 import Web3

def compile_source_file(file_path):
    with open(file_path, 'r') as f:
        source = f.read()
    return compile_source(source)


def deploy_contract(web3: Web3, contract_interface):
    address = web3.eth.accounts[0]
    tx_hash = web3.eth.contract(
        abi=contract_interface["abi"],
        bytecode=contract_interface['bin']).constructor().transact({'from': address})
    address = web3.eth.get_transaction_receipt(tx_hash)['contractAddress']
    return address


class Contract:

    def __init__(self, contract_source, web3, contract_address=""):

        self.message_log = []
        self.pub_keychain = []
        self.cipher_keychain = []

        self.web3 = web3
        self.contract_source_path = contract_source

        self.compiled_sol = compile_source_file(self.contract_source_path)
        self.contract_id, self.contract_interface = self.compiled_sol.popitem()

        if contract_address == "":
            self.contract_address = str(deploy_contract(self.web3, self.contract_interface))
        else:
            self.contract_address = contract_address

        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_interface["abi"])
    
    # Message functions

    def get_number_of_messages(self):
        return self.contract.functions.get_message_state().call()
    
    def get_message_by_number(self, n):
        return self.contract.functions.get_message_by_number(n).call()
    
    def add_message(self, msg):
        return self.contract.functions.add_message(msg).transact()
    
    # Pubkey functions

    def get_number_of_pub_keys(self):
        return self.contract.functions.get_pub_key_state().call()
    
    def get_pub_key_by_number(self, n):
        return self.contract.functions.get_pub_key_by_number(n).call()
    
    def add_pub_key(self, pub_key):
        return self.contract.functions.add_pub_key(pub_key).transact()

    # Keycipher functions

    def get_number_of_key_ciphers(self):
        return self.contract.functions.get_key_cipher_state().call()
    
    def get_key_cipher_by_number(self, n):
        return self.contract.functions.get_key_cipher_by_number(n).call()
    
    def add_key_cipher(self, key_cipher):
        return self.contract.functions.add_key_cipher(key_cipher).transact()