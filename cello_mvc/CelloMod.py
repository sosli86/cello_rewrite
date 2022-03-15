from cello_mvc.CelloDB import CelloDB
from gnupg import GPG
from cello_mvc.Contract import Contract
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
    def __init__(self, db: CelloDB, user_name, web3, user_address, gpghome):
        self.user_name = user_name
        self.web3 = web3
        self.db = db

        # Initialize database and gnupg
        self.gpg = GPG(gnupghome=gpghome)

        # Try to find user address in the database
        try:
            self.user_address = self.db.select_x_from_y_where_z("user_address", "user", f'user_name = ("{ user_name }")')[0][0]
        except:
            print("Didn't find user address.")
            self.user_address = user_address
            self.db.insert_into_x_values_y("user", f'("{user_name}"), ("{user_address}")')
        
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
    
    def init_contracts_from_database(self):
        contracts = self.db.select_x_from_y_where_z("*", "contract")
        for contract in contracts:
            new_contract = ActiveContract(self.web3, contract[1], contract[0])
            self.contracts[contract[1]] = new_contract
            print("added " + contract[1] + ": " + contract[0])
        return contracts
    
    def init_user_pub_key(self, password):
        self.key = self.gpg.export_keys(self.user_name)
        if self.key=='':
            input_data = self.gpg.gen_key_input(key_type="RSA", key_length=4096, name_email=f'{self.user_name}@cello', passphrase=password)
            self.gpg.gen_key(input_data)
            self.key = self.gpg.export_keys(self.user_name)
        return self.key

    def populate_contract_keys_from_database(self):
        self.contract_list_authenticated = self.db.select_x_from_y_where_z("contract_name, user_key_cipher", "membership", f'user_name = ("{self.user_name}")')
        try:
            for contract in self.contract_list_authenticated:
                contract_key_cipher = contract[1]
                contract_key = str(self.gpg.decrypt(contract_key_cipher))
                self.contract_keys[contract[0]] = contract_key
        except:
            print("...")
        
    def populate_message_archives_from_database(self):
        try:
            for contract in self.contract_list_authenticated:
                self.contract_message_archives[contract] = self.get_message_archive(contract)
        except:
            print("...")
    
    def populate_membership_archives_from_database(self):
        try:
            for contract in self.contract_list_authenticated:
                self.contract_membership_archives[contract] = self.get_membership_archive(contract)
        except:
            print("...")
    
    def init_authenticated_contracts(self):
        # Initialize authenticated contracts
        for contract_name in self.contract_keys.keys():
            contract_address = self.model.db.select_x_from_y_where_z("contract_address", "contract", f'contract_name = { contract_name }')[0]
            self.contracts[contract_name] = ActiveContract(self.web3, contract_name, contract_address)
    
    def init_update_loop(self):
        # Initialize update loop for authenticated contracts
        update_thread = Thread(target=self.update_loop)
        update_thread.start()
    
    def init_authentication_loop(self):
        # Initialize authentication loop for unauthenticated contracts
        authentication_thread = Thread(target=self.authentication_loop)
        authentication_thread.start()
        
    def get_message_archive(self, contract_name):
        message_archive = self.db.select_x_from_y_where_z("contents", "message", f'contract_name = ("{ contract_name }")')
        return message_archive
    
    def get_membership_archive(self, contract_name):
        membership_archive = self.db.select_x_from_y_where_z("user_name, user_pub_key, user_key_cipher", "membership", f'contract_name = ("{ contract_name }")')
        return membership_archive
    
    def add_message_to_contract(self, contract_name, msg_plaintext):
        seconds = time.time()
        current_time = time.ctime(seconds)
        msg = f'{ current_time }--{ self.user_name }@{ contract_name }: { msg_plaintext }'
        msg_ciphertext = str(self.gpg.encrypt(msg, symmetric='AES256', recipients=None, armor=False, passphrase=self.contract_keys[contract_name]))
        return self.contracts[contract_name].add_message(msg_ciphertext)
    
    def add_pub_key_to_contract(self, contract_name, pub_key):
        return self.contracts[contract_name].add_pubkey(pub_key)
    
    def add_key_cipher_to_contract(self, contract_name, key_cipher):
        self.contracts[contract_name].add_keycipher(key_cipher)
    
    def update_messages_from_contract(self, contract_name):
        new_message_log = []
        try:
            number_of_messages = len(self.contract_message_archives[contract_name])
            new_message_ciphers = self.contracts[contract_name].get_all_new_messages(number_of_messages)
        except:
            self.contract_message_archives[contract_name] = []
            self.contract_message_logs[contract_name] = []
            new_message_ciphers = self.contracts[contract_name].get_all_new_messages(0)
        while len(new_message_ciphers) >  0:
            new_message = str(self.gpg.decrypt(new_message_ciphers.pop(0), passphrase=self.contract_keys[contract_name])) 
            print(new_message)
            new_message_log.append(new_message)
            self.contract_message_logs[contract_name].append(new_message)
        return new_message_log

    def update_pub_keys_from_contract(self, contract_name):
        try:
            number_of_stored_pubkeys = len(self.contract_pub_key_logs[contract_name])
            new_pub_keys = self.contracts[contract_name].get_all_new_pubkeys(number_of_stored_pubkeys)
        except:
            self.contract_pub_key_logs[contract_name] = []
            new_pub_keys = self.contracts[contract_name].get_all_new_pubkeys(0)
        while len(new_pub_keys) > 0:
            self.contract_pub_key_logs[contract_name].append(new_pub_keys.pop(0))
            self.gpg.import_keys(self.contract_pub_key_logs[contract_name][-1])
            for key in self.gpg.list_keys():
                if self.contract_pub_key_logs[contract_name][-1] == self.gpg.export_keys(key["uids"][0]):
                    new_member_name = key["uids"][0]
            new_key_cipher = str(self.gpg.encrypt(self.contract_keys[contract_name], new_member_name))
            self.contracts[contract_name].add_keycipher(new_key_cipher)

    def update_key_ciphers_from_contract(self, contract_name):
        try:
            number_of_stored_key_ciphers = len(self.contract_key_cipher_logs[contract_name])
        except:
            self.contract_key_cipher_logs[contract_name] = []
            number_of_stored_key_ciphers = 0
        new_key_ciphers = self.contracts[contract_name].get_all_new_keyciphers(number_of_stored_key_ciphers)
        while len(new_key_ciphers) > 0:
            self.contract_key_cipher_logs[contract_name].append(new_key_ciphers.pop(0))
            new_key_cipher = self.contract_key_cipher_logs[contract_name][-1]
            new_key_cipher_recipient = self.gpg.get_recipients(new_key_cipher)[0]
            for key in self.gpg.list_keys():
                if key["keyid"] == new_key_cipher_recipient:
                    self.write_new_membership_to_database(contract_name, key["uids"][0], self.gpg.export_keys(key["keyid"]), new_key_cipher)
                if self.user_name in key["uids"]:
                    return True
                else:
                    return False
    
    def check_for_validation(self, contract_name):
        for key in self.gpg.list_keys():
            if self.user_name in key["uids"]:
                user_key = key
        
        for key_cipher in self.contract_key_cipher_logs[contract_name]:
            contract_key = str(self.gpg.decrypt(key_cipher))
            if contract_key != '':
                self.contract_key_cipher_logs[contract_name] = contract_key
    
    def write_message_logs_to_database(self, contract_name):
        while len(self.contract_message_logs[contract_name]) > 0:
            new_message = self.contract_message_logs[contract_name].pop(0)
            print(new_message)
            self.db.insert_into_x_values_y("message", f'("{ contract_name }"), ("{ new_message }")')
    
    def write_new_membership_to_database(self, contract_name, new_user_name, new_user_pub_key, new_user_key_cipher):
        self.db.insert_into_x_values_y("membership", f'("{ new_user_name }"), ("{ contract_name }"), ("{ new_user_pub_key }"), ("{ new_user_key_cipher }")')
    
    def write_contract_to_database(self, contract_name, contract_address):
        self.db.insert_into_x_values_y("contract", f'("{ contract_address }"), ("{ contract_name }")')
    
    def update_loop(self):
        while True:
            try:
                for contract in self.contracts.keys():
                    self.update_messages_from_contract(contract)
                    self.update_pub_keys_from_contract(contract)
                    self.update_key_ciphers_from_contract(contract)
            except:
                print("Nothing for update_loop to do.")
            time.sleep(1)
    
    def authentication_loop(self):
        while True:
            try:
                for n in range (self.contract_list_unauthenticated):
                    if self.update_key_ciphers_from_contract(self.contract_list_unauthenticated[n]):
                        self.contract_list_authenticated.append(self.contract_list_unauthenticated.pop(n))
            except:
                print("Nothing for authentication_loop to do.")
            time.sleep(1)
    
    def get_contracts_dict(self):
        return self.contracts