import os
import unittest
from cello_mvc.CelloMod import *
from cello_mvc.CelloDB import CelloDB
from cello_mvc.CelloCryptog import *
from cello_mvc.CelloControl import get_web3

class TestUserMod(unittest.TestCase):
    def setUp(self):
        web3 = get_web3()

        users = ["Sophia", "Olivia", "Yael"]
        self.user_addresses = {}
        for i in range (0, len(users)):
            self.user_addresses[users[i]] = web3.eth.accounts[i]

        keyring_root = "./test/integration/fixtures/keyring_test_"
        self.keyrings = []
        for i in range(0, len(users)):
            keyring_path = keyring_root + (''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for j in range(8)))
            os.mkdir(keyring_path)
            keyring = CelloKeyring(keyring_path)
            keyring.generate_keypair()
            keyring.open_keypair()
            self.keyrings.append(keyring)

        db_root = "./test/integration/fixtures/db_test_"
        self.dbs = []
        for i in range(0, len(users)):
            db_path = db_root + (''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for j in range(8))) + ".db"
            self.dbs.append(CelloDB(db_path))
            self.dbs[i].new_database()
        
        contract_names = ["Cello World", "Big Bad Boobies"]
        self.contracts = {}
        self.contract_keys = {}
        for i in range(0, len(contract_names)):
            self.contracts[contract_names[i]] = ActiveContract(web3, contract_names[i])
            self.contract_keys[contract_names[i]] = contract_key_gen()

        self.mods = []
        for i in range(0, len(users)):
            self.mods.append(UserMod())
            self.mods[i].set_web3(web3)
            self.mods[i].set_db(self.dbs[i])
            self.mods[i].set_keyring(self.keyrings[i])
            self.mods[i].new_user(users[i], self.user_addresses[users[i]])
            for contract_name in self.contracts.keys():
                self.mods[i].contracts[contract_name] = self.contracts[contract_name]

    def test_set_contract_key(self):
        for contract_name in self.contracts.keys():
            for mod in self.mods:
                contract_key = self.contract_keys[contract_name]
                mod.set_contract_key(contract_name, contract_key)
                expected = contract_key
                result = mod.contract_keys[contract_name]
                self.assertEqual(expected, result, "test_set_contract_key: didn't set contract key.")
    
    def test_set_db(self):
        for i in range(0, len(self.mods)):
            self.mods[i].set_db(self.dbs[i])
            expected = self.dbs[i]
            result = self.mods[i].db
            self.assertEqual(expected, result, "test_set_db: database was not set.")

    def test_new_user(self):
        for i in range(0, len(self.mods)):
            self.mods[i].set_db(self.dbs[i])
        c = 0
        for user_name in self.user_addresses.keys():
            self.mods[c].new_user(user_name, self.user_addresses[user_name])
            expected = self.user_addresses[user_name]
            result = self.mods[c].db.select_x_from_y_where_z("user_address", "user", f'user_name = ("{user_name}")')[0][0]
            self.assertEqual(expected, result, "test_new_user: user address not found in database.")
    
    def test_set_keyring(self):
        for i in range(0, len(self.mods)):
            self.mods[i].set_keyring(self.keyrings[i])
            expected = self.keyrings[i]
            result = self.mods[i].keyring
            self.assertEqual(expected, result, "test_set_keyring: keyring not set.")
    
    def test_write_contract_to_database(self):
        for i in range(0, len(self.mods)):
            self.mods[i].set_db(self.dbs[i])

        for mod in self.mods:
            for contract_name in self.contracts.keys():
                contract_address = self.contracts[contract_name].contract_address
                expected = contract_address
                mod.write_contract_to_database(contract_name, contract_address)
                result = mod.db.select_x_from_y_where_z("contract_address", "contract", f'contract_name = ("{contract_name}")')[0][0]
                self.assertEqual(expected, result, "test_write_contract_to_database: database not written to contract.")
    
    def test_init_contracts_from_database(self):
        for i in range(0, len(self.mods)):
            self.mods[i].set_db(self.dbs[i])

        for mod in self.mods:
            for contract_name in self.contracts.keys():
                contract_address = self.contracts[contract_name].contract_address
                mod.write_contract_to_database(contract_name, contract_address)
        
        for mod in self.mods:
            mod.init_contracts_from_database()
            result = mod.contracts.keys()
            expected = self.contracts.keys()
            self.assertEqual(expected, result, "test_init_contracts_from_database: contracts not initialized.")

    
    def test_write_new_membership_to_database(self):
        for mod in self.mods:
            for contract_name in self.contracts.keys():
                pub_key = mod.keyring.pack_pubkey()
                key_cipher = mod.keyring.encrypt_contract_key(self.contract_keys[contract_name])
                mod.write_new_membership_to_database(contract_name, mod.user_name, pub_key, key_cipher)
                expected = (contract_name, pub_key, key_cipher)
                result = mod.db.select_x_from_y_where_z("contract_name, user_pub_key, user_key_cipher", "membership", f'user_name = ("{mod.user_name}") and contract_name = ("{contract_name}")')[0]
                self.assertEqual(expected, result, "test_write_new_membership_to_database: membership info not written to database.")
    
    def test_populate_contract_keys_from_database(self):
        for mod in self.mods:
            for contract_name in self.contracts.keys():
                pub_key = mod.keyring.pack_pubkey()
                key_cipher = mod.keyring.encrypt_contract_key(self.contract_keys[contract_name])
                mod.write_new_membership_to_database(contract_name, mod.user_name, pub_key, key_cipher)
                mod.populate_contract_keys_from_database()
                expected = self.contract_keys[contract_name]
                result = mod.contract_keys[contract_name]
                self.assertEqual(expected, result, "test_populate_contract_keys_from_database: failed to initialize contract keys from database.")

    def test_populate_message_archives_from_database(self):
        web3 = get_web3()
        



#    def test_add_pub_key_to_contract(self):

#    def test_add_key_cipher_from_contract(self):

#    def test_update_messages_from_contract(self):

#    def test_update_pub_keys_from_contract(self):

#    def test_validate_user(self):

#    def test_update_key_ciphers_from_contract(self):

#    def test_write_message_logs_to_database(self):

#    def test_write_new_membership_to_database(self):

#    def test_write_contract_to_database(self):