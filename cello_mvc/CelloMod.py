from cello_mvc.CelloDB import CelloDB
from cello_mvc.Contract import Contract
from cello_mvc.CelloCryptog import CelloKeyring, contract_key_gen, decrypt_message, encrypt_message
from threading import *
import time

class ActiveContract:
    def __init__(self, web3, contract_name, contract_address=""):
        self.web3 = web3
        self.name = contract_name
        self.contract = Contract("cello_mvc/Contact.sol", self.web3, contract_address)
        self.contract_address = self.contract.contract_address
    
    # Message functions

    def get_all_new_messages(self, number_of_messages=0):
        new_message_ciphers = []
        for n in range(number_of_messages, self.contract.get_number_of_messages()):
            new_message_ciphers.append(self.contract.get_message_by_number(n))
        return new_message_ciphers
    
    def add_message(self, msg):
        return self.contract.add_message(msg)
    
    # Pubkey functions

    def get_all_new_pubkeys(self, number_of_pubkeys=0):
        new_pubkeys = []
        for n in range(number_of_pubkeys, self.contract.get_number_of_pub_keys()):
            new_pubkeys.append(self.contract.get_pub_key_by_number(n))
        return new_pubkeys
    
    def add_pubkey(self, pubkey):
        return self.contract.add_pub_key(pubkey)
    
    # Keycipher functions

    def get_all_new_keyciphers(self, number_of_keyciphers=0):
        new_keyciphers = []
        for n in range(number_of_keyciphers, self.contract.get_number_of_key_ciphers()):
            new_keyciphers.append(self.contract.get_key_cipher_by_number(n))
        return new_keyciphers
    
    def add_keycipher(self, keycipher):
        return self.contract.add_key_cipher(keycipher)

class UserMod:
    def __init__(self):
        
        # Initialize contract dictionaries
        self.contracts = {}
        self.contract_keys = {}
        self.contract_message_logs = {}
        self.contract_pub_key_logs = {}
        self.contract_key_cipher_logs = {}
        self.contract_message_archives = {}
        self.contract_membership_archives = {}

        self.contract_membership_authenticated = []
        self.contract_membership_unauthenticated = []
    
    def set_web3(self, web3):
        self.web3 = web3
    
    def set_contract_key(self, contract_name, contract_key):
        self.contract_keys[contract_name] = contract_key
    
    def set_db(self, db: CelloDB):
        self.db = db
    
    def set_keyring(self, keyring: CelloKeyring):
        self.keyring = keyring
    
    def new_user(self, user_name, user_address):
        self.user_name = user_name
        self.db.insert_into_x_values_y("user", f'("{user_name}"), ("{user_address}")')
    
    def init_contracts_from_database(self):
        contracts = self.db.select_x_from_y_where_z("*", "contract")
        for contract in contracts:
            new_contract = ActiveContract(self.web3, contract[1], contract[0])
            self.contracts[contract[1]] = new_contract
            self.contract_message_logs[contract[1]] = []
            self.contract_pub_key_logs[contract[1]] = []
            self.contract_key_cipher_logs[contract[1]] = []
            self.contract_message_archives[contract[1]] = []
            print("added " + contract[1] + ": " + contract[0])
        return contracts

    def populate_contract_keys_from_database(self):
        self.contract_list_authenticated = self.db.select_x_from_y_where_z("contract_name, user_key_cipher", "membership", f'user_name = ("{self.user_name}")')
        try:
            for contract in self.contract_list_authenticated:
                contract_key_cipher = contract[1]
                self.contract_keys[contract[0]] = self.keyring.decrypt_contract_key(contract_key_cipher)
        except:
            print("...")
        
    def populate_message_archives_from_database(self):
        for contract in self.contract_membership_authenticated:
            message_archive = []
            for message in self.db.select_x_from_y_where_z("contents", "message", f'contract_name = ("{contract}")'):
                message_archive.append(message)
            self.contract_message_archives[contract] = message_archive

    
    def init_authentication_loop(self):
        # Initialize authentication loop for unauthenticated contracts
        authentication_thread = Thread(target=self.authentication_loop)
        authentication_thread.start()
    
    def get_membership_archive(self, contract_name):
        membership_archive = self.db.select_x_from_y_where_z("user_name, user_pub_key, user_key_cipher", "membership", f'contract_name = ("{ contract_name }")')
        return membership_archive
    
    def add_message_to_contract(self, contract_name, msg_plaintext):
        seconds = time.time()
        current_time = time.ctime(seconds)
        msg = f'{ current_time }--{ self.user_name }@{ contract_name }: { msg_plaintext }'
        msg_ciphertext = encrypt_message(msg, self.contract_keys[contract_name])
        return self.contracts[contract_name].add_message(msg_ciphertext)
    
    def add_pub_key_to_contract(self, contract_name, pub_key):
        return self.contracts[contract_name].add_pubkey(pub_key)
    
    def add_key_cipher_to_contract(self, contract_name, key_cipher):
        self.contracts[contract_name].add_keycipher(key_cipher)
    
    def update_messages_from_contract(self, contract_name):
        try:
            number_of_messages = len(self.contract_message_archives[contract_name])
            new_message_ciphers = self.contracts[contract_name].get_all_new_messages(number_of_messages)
        except:
            new_message_ciphers = self.contracts[contract_name].get_all_new_messages(0)
        while len(new_message_ciphers) >  0:
            new_message_cipher = new_message_ciphers.pop(0)
            new_message = decrypt_message(new_message_cipher.encode(), self.contract_keys[contract_name])
            self.contract_message_logs[contract_name].append(new_message)

    def update_pub_keys_from_contract(self, contract_name):
        try:
            number_of_stored_pubkeys = len(self.contract_pub_key_logs[contract_name])
            new_pub_keys = self.contracts[contract_name].get_all_new_pubkeys(number_of_stored_pubkeys)
        except:
            self.contract_pub_key_logs[contract_name] = []
            new_pub_keys = self.contracts[contract_name].get_all_new_pubkeys(0)
        while len(new_pub_keys) > 0:
            new_public_key = new_pub_keys.pop(0)
            new_user_name = new_public_key.split('\n')[0]
            self.contract_pub_key_logs[contract_name].append(new_pub_keys.pop(0))
            self.keyring.store_new_public_key(self.contract_pub_key_logs[contract_name][-1])
            self.validate_user(new_user_name, contract_name)
        
    def validate_user(self, new_user_name, contract_name):
        new_contract_key_cipher = self.keyring.encrypt_contract_key(self.contract_keys[contract_name], new_user_name)
        self.contracts[contract_name].add_keycipher(new_contract_key_cipher)

    def update_key_ciphers_from_contract(self, contract_name):
        try:
            self.contract_keys[contract_name]
            authenticated = True
        except:
            authenticated = False
        try:
            number_of_stored_key_ciphers = len(self.contract_key_cipher_logs[contract_name])
        except:
            self.contract_key_cipher_logs[contract_name] = []
            number_of_stored_key_ciphers = 0
        new_key_ciphers = self.contracts[contract_name].get_all_new_keyciphers(number_of_stored_key_ciphers)
        while len(new_key_ciphers) > 0:
            self.contract_key_cipher_logs[contract_name].append(new_key_ciphers.pop(0))
            new_key_cipher = self.contract_key_cipher_logs[contract_name][-1]
            if not authenticated:
                recipient_name_cipher = new_key_cipher.split('\n')[0]
                try:
                    recipient_name = self.keyring.decrypt_contract_key(recipient_name_cipher)
                    if recipient_name == self.user_name:
                        contract_key = self.keyring.decrypt_contract_key(new_key_cipher.split('\n')[1])
                        self.contract_keys[contract_name] = contract_key
                        authenticated = True
                except:
                    pass
        return authenticated
    
    def write_message_logs_to_database(self, contract_name):
        while len(self.contract_message_logs[contract_name]) > 0:
            new_message = self.contract_message_logs[contract_name].pop(0)
            self.db.insert_into_x_values_y("message", f'("{ contract_name }"), ("{ new_message }")')
    
    def write_new_membership_to_database(self, contract_name, new_user_name, new_user_pub_key, new_user_key_cipher):
        self.db.insert_into_x_values_y("membership", f'("{ new_user_name }"), ("{ contract_name }"), ("{ new_user_pub_key }"), ("{ new_user_key_cipher }")')
    
    def write_contract_to_database(self, contract_name, contract_address):
        self.db.insert_into_x_values_y("contract", f'("{ contract_address }"), ("{ contract_name }")')