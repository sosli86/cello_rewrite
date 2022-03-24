import os
import unittest
from cello_mvc.CelloMod import *
from cello_mvc.CelloDB import CelloDB
from cello_mvc.CelloCryptog import *
from cello_mvc.CelloControl import get_web3

class TestUserMod(unittest.TestCase):
    def test_populate_message_archives_from_database(self):
        web3 = get_web3()

        # initialize user
        user_name = "test_user"
        user_address = web3.eth.accounts[0]

        # initialize database
        try:
            os.remove("./test/integration/fixtures/test_populate_message_archives_from_database.db")
        except:
            pass
        db = CelloDB("./test/integration/fixtures/test_populate_message_archives_from_database.db")
        db.new_database()

        # initialize user keyring
        try:
            os.remove("./test_integration/fixtures/test_full_model_cycle/user_keyring/public_key.pem")
            os.remove("./test_integration/fixtures/test_full_model_cycle/user_keyring/private_key.pem")
        except:
            pass
        user_keyring = CelloKeyring("./test_integration/fixtures/test_full_model_cycle/user_keyring")
        user_keyring.generate_keypair()
        user_keyring.open_keypair()

        # initialize contract keyring
        contract_keyring = ContractKeyring("./test_integration/fixtures/test_full_model_cycle/contract_keyring")

        # initialize contract
        contract_name = "big bad boobies"
        contract = ActiveContract(web3, contract_name)
        contract_address = contract.contract_address
        contract_key 

        # initialize model
        model = UserMod()

        model.set_keyring(keyring)
        self.assertEqual(keyring, model.keyring, "set_keyring failed."))

        model.set_db(db)
        self.assertEqual(db, model.db, "set_db failed.")

        model.set_web3(web3)
        self.assertEqual(web3, model.web3, "set_web3 failed.")

        # write new user to database
        model.new_user(user_name, user_address)
        expected = (user_name, user_address)
        result = model.db.select_x_from_y_where_z("*", "user")[0]
        self.assertEqual(expected, result, "new_user failed.")

        # write new contract to database
        model.write_contract_to_database(contract_name, contract_address)
        expected = (contract_name, contract_address)
        result = model.db.select_x_from_y_where_z("*", "contract")[0]
        self.assertEqual(expected, result, "write_contract_to_database failed.")

        # add contract key to keyring
        model.set_contract_key(contract_name, contract_key)
        self.assertEqual(expected, result, "set_contract_key failed.")

        # 



#    def test_add_pub_key_to_contract(self):

#    def test_add_key_cipher_from_contract(self):

#    def test_update_messages_from_contract(self):

#    def test_update_pub_keys_from_contract(self):

#    def test_validate_user(self):

#    def test_update_key_ciphers_from_contract(self):

#    def test_write_message_logs_to_database(self):

#    def test_write_new_membership_to_database(self):

#    def test_write_contract_to_database(self):