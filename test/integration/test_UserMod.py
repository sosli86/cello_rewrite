import unittest
import gnupg
import os
import secrets
import string
import shutil

from cello_mvc.CelloMod import UserMod, ActiveContract
from cello_mvc.CelloDB import CelloDB
from cello_mvc.CelloControl import get_web3


class TestUserMod(unittest.TestCase):
    def setUp(self):
        try:
            shutil.rmtree("test/integration/fixtures/gpg/")
        except:
            pass
        os.mkdir("test/integration/fixtures/gpg/")
        try:
            os.remove("test/integration/fixtures/test_usermod.db")
        except:
            pass
        self.db = CelloDB("test/integration/fixtures/test_usermod.db")
        self.db.new_database()
        self.web3 = get_web3()
        self.user_address = self.web3.eth.accounts[0]
        self.active_contract = ActiveContract(self.web3, "test_contract")
        self.model = UserMod(self.db, "test_user", self.web3, self.user_address, "test/integration/fixtures/gpg/")
    
    def test_init(self):
        expected = (f'{self.user_address}',)
        result = self.db.select_x_from_y_where_z("user_address", "user", "user_name = ('test_user')")[0]
        self.assertEqual(expected, result, "Failed to commit user to DB.")
    
    def init_user_pub_key(self):
        result = self.model.init_user_pub_key("password")
        expected = self.gpg.export_keys("test_user")
        self.assertIsNotNone(result, "failed to generate user pub key.")
        self.assertEqual(expected, result, "failed to init user pub key.")
    
    def test_write_contract_to_database(self):
        self.model.write_contract_to_database("test_contract", self.active_contract.contract_address)
        expected = self.active_contract.contract_address
        result = self.db.select_x_from_y_where_z("contract_address", "contract", "contract_name = ('test_contract')")[0][0]
        self.assertEqual(expected, result, "Couldn't write contract to database.")
    
    def test_write_new_membership_to_database(self):
        self.model.write_new_membership_to_database("test_contract", "test_user", "test_pub_key", "test_key_cipher")
        expected = ("test_user", "test_contract", "test_pub_key", "test_key_cipher")
        result = self.db.select_x_from_y_where_z("*", "membership")[0]
        self.assertEqual(expected, result, "Couldn't write membership to database.")        
    
    def test_init_contracts_from_database(self):
        self.model.write_contract_to_database("test_contract", self.active_contract.contract_address)
        self.model.init_contracts_from_database()
        expected = self.active_contract.contract_address
        result = self.model.get_contracts_dict()["test_contract"].contract_address
        self.assertEqual(expected, result, "Couldn't init contracts from database.")
    
    def test_populate_contract_keys_from_database(self):
        contract_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(128))
        pub_key = self.model.init_user_pub_key("password")
        test_key_cipher = str(self.model.gpg.encrypt(contract_key, "test_user"))
        self.model.write_contract_to_database("test_contract", self.active_contract.contract_address)
        self.model.write_new_membership_to_database("test_contract", "test_user", pub_key, test_key_cipher)
        self.model.populate_contract_keys_from_database()
        result = self.model.contract_keys["test_contract"]
        self.assertEqual(contract_key, result, "Couldn't populate keyring from database.")
    
    def test_add_message(self)
        contract_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(128))
        pub_key = self.model.init_user_pub_key("password")
        test_key_cipher = str(self.model.gpg.encrypt(contract_key, "test_user"))
        self.model.write_contract_to_database("test_contract", self.active_contract.contract_address)
        self.model.write_new_membership_to_database("test_contract", "test_user", pub_key, test_key_cipher)
        self.model.populate_contract_keys_from_database()
        self.model.init_contracts_from_database()