from cello_mvc.CelloCryptog import *
import unittest
import time
import datetime

class TestKeyFunctions(unittest.TestCase):
    def setUp(self):
        time.sleep(1)
        self.current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if not exists('./test/integration/fixtures/contract_keyring_test/'):
            os.mkdir('./test/integration/fixtures/contract_keyring_test/')
        contract_keyring_path = f'./test/integration/fixtures/contract_keyring_test/{self.current_time}'
        os.mkdir(contract_keyring_path)

        contract_name = self.current_time
        self.contract_keyring = ContractKeyring(contract_keyring_path)
        self.contract_keyring.contract_key_gen(contract_name)
        with open(contract_keyring_path + f'/{contract_name}/contract.key', "r") as f:
            contract_keyring = f.read()
        self.assertIsNotNone(contract_keyring, "ContractKeyring: failed to generate contract key.")

        user_name_1 = "test_user_1"
        if not exists('./test/integration/fixtures/user_keyring_1_test'):
            os.mkdir('./test/integration/fixtures/user_keyring_1_test')
        user_keyring_path_1 = f'./test/integration/fixtures/user_keyring_1_test/{self.current_time}'
        self.user_keyring_1 = CelloKeyring(user_keyring_path_1)
        self.user_keyring_1.set_user_name(user_name_1)
        self.assertEqual(user_name_1, self.user_keyring_1.user_name, "CelloKeyring-1: failed to set username.")

        user_name_2 = "test_user_2"
        if not exists('./test/integration/fixtures/user_keyring_2_test'):
            os.mkdir('./test/integration/fixtures/user_keyring_2_test')
        user_keyring_path_2 = f'./test/integration/fixtures/user_keyring_2_test/{self.current_time}'
        self.user_keyring_2 = CelloKeyring(user_keyring_path_2)
        self.user_keyring_2.set_user_name(user_name_2)
        self.assertEqual(user_name_2, self.user_keyring_2.user_name, "CelloKeyring-2: failed to set username.")
    
    def test_CelloKeyring_generate_keypair(self):
        self.user_keyring_1.generate_keypair()
        with open(self.user_keyring_1.keyring_path + "/private_key.pem") as f:
            private_key = f.read()
        self.assertIsNotNone(private_key, "CelloKeyring-1: failed to generate private key.")
        with open(self.user_keyring_1.keyring_path + "/public_key.pem") as f:
            public_key = f.read()
        self.assertIsNotNone(public_key, "CelloKeyring-1: failed to generate public key.")

        self.user_keyring_2.generate_keypair()        
        with open(self.user_keyring_2.keyring_path + "/private_key.pem") as f:
            private_key = f.read()
        self.assertIsNotNone(private_key, "CelloKeyring-2: failed to generate private key.")
        with open(self.user_keyring_2.keyring_path + "/public_key.pem") as f:
            public_key = f.read()
        self.assertIsNotNone(public_key, "CelloKeyring-2: failed to generate public key.")

    def test_CelloKeyring_open_keypair(self):
        self.user_keyring_1.generate_keypair()
        self.user_keyring_1.open_keypair()
        self.assertIsNotNone(self.user_keyring_1.private_key, "CelloKeyring-1: failed to open private key.")
        self.assertIsNotNone(self.user_keyring_1.public_key, "CelloKeyring-1: failed to open private key.")

        self.user_keyring_2.generate_keypair()
        self.user_keyring_2.open_keypair()
        self.assertIsNotNone(self.user_keyring_2.private_key, "CelloKeyring-2: failed to open private key.")
        self.assertIsNotNone(self.user_keyring_2.public_key, "CelloKeyring-2: failed to open private key.")

    def test_CelloKeyring_pack_pubkey(self):
        self.user_keyring_1.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        dummy_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(32))
        expected = [self.user_keyring_1.user_name, dummy_key]
        result = packed_pubkey_1.split(":::::")
        self.assertListEqual(expected, result, "CelloKeyring-1: failed to pack pubkey.")

        self.user_keyring_2.generate_keypair()
        packed_pubkey_2 = self.user_keyring_2.pack_pubkey()
        expected = [self.user_keyring_2.user_name, dummy_key]
        result = packed_pubkey_2.split(":::::")
        self.assertListEqual(expected, result, "CelloKeyring-2: failed to pack pubkey.")
    
    def test_ContractKeyring_list_contracts(self):
        expected = [f'{self.current_time}']
        result = self.contract_keyring.list_contracts()
        self.assertListEqual(expected, result, "ContractKeyring.list_contracts failed to list contracts.")
    
    def test_ContractKeyring_import_user_key(self):
        self.user_keyring_1.generate_keypair()
        self.user_keyring_2.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        packed_pubkey_2 = self.user_keyring_2.pack_pubkey()

        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_1)
        with open(self.contract_keyring.keyring_path + f'/{self.current_time}/' + self.user_keyring_1.user_name + ".pem") as f:
            self.assertGreater(len(f.read()), 400, "ContractKeyring.import_user_key: failed to import test_user 1's key.")        
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_2)
        with open(self.contract_keyring.keyring_path + f'/{self.current_time}/' + self.user_keyring_2.user_name + ".pem") as f:
            self.assertGreater(len(f.read()), 400, "ContractKeyring.import_user_key: failed to import test_user 2's key.")

    def test_ContractKeyring_encrypt_contract_key(self):
        self.user_keyring_1.generate_keypair()
        self.user_keyring_2.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        packed_pubkey_2 = self.user_keyring_2.pack_pubkey()
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_1)
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_2)

        self.contract_keyring.encrypt_contract_key(f'{self.current_time}', "test_user_1")
        with open(self.contract_keyring.keyring_path + f'/{self.current_time}/test_user_1.cyph') as f:
            key_cipher_1 = f.read()
        key_cipher_1_length = len(key_cipher_1)
        self.assertGreater(key_cipher_1_length, 30, "ContractKeyring.encrypt_contract_key: failed to encrypt contract key for test_user_1.")

        self.contract_keyring.encrypt_contract_key(f'{self.current_time}', "test_user_2")
        with open(self.contract_keyring.keyring_path + f'/{self.current_time}/test_user_2.cyph') as f:
            key_cipher_2 = f.read()
        key_cipher_2_length = len(key_cipher_2)
        self.assertGreater(key_cipher_2_length, 30, "ContractKeyring.encrypt_contract_key: failed to encrypt contract key for test_user_2.")

    def test_ContractKeyring_list_unauthenticated_contract_members(self):
        self.user_keyring_1.generate_keypair()
        self.user_keyring_2.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        packed_pubkey_2 = self.user_keyring_2.pack_pubkey()
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_1)
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_2)
        member_list = self.contract_keyring.list_unauthenticated_contract_members(f'{self.current_time}')
        expected = ["test_user_1", "test_user_2"]
        self.assertListEqual(expected, member_list, "ContractKeyring.list_contract_members: failed to list contract members.")
    
    def test_ContractKeyring_get_contract_key(self):
        self.contract_keyring.contract_key_gen("test_contract_2")
        contract_key_2 = self.contract_keyring.get_contract_key("test_contract_2")
        self.assertGreater(len(contract_key_2), 20, "ContractKeyring.get_contract_key: failed to retrieve contract key.")
    
    def test_CelloKeyring_decrypt_key_cipher(self):
        self.user_keyring_1.generate_keypair()
        self.user_keyring_2.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        packed_pubkey_2 = self.user_keyring_2.pack_pubkey()
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_1)
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_2)

        key_cipher_1 = self.contract_keyring.encrypt_contract_key(f'{self.current_time}', "test_user_1")
        key_cipher_2 = self.contract_keyring.encrypt_contract_key(f'{self.current_time}', "test_user_2")

        contract_key = self.contract_keyring.get_contract_key(f'{self.current_time}')

        key_plaintext_1 = self.user_keyring_1.decrypt_key_cipher(key_cipher_1)
        self.assertEqual(key_plaintext_1, contract_key, "CelloKeyring.decrypt_key_cipher: failed to decrypt key_cipher_1.")

        key_plaintext_2 = self.user_keyring_2.decrypt_key_cipher(key_cipher_2)
        self.assertEqual(key_plaintext_2, contract_key, "CelloKeyring.decrypt_key_cipher: failed to decrypt key_cipher_2.")
    
    def test_ContractKeyring_import_contract_key(self):
        self.user_keyring_1.generate_keypair()
        packed_pubkey_1 = self.user_keyring_1.pack_pubkey()
        self.contract_keyring.import_user_key(f'{self.current_time}', packed_pubkey_1)
        
        contract_keyring_2 = ContractKeyring("./test/integration/fixtures/contract_keyring_test_2")

        key_cipher_1 = self.contract_keyring.encrypt_contract_key(f'{self.current_time}', "test_user_1")

        key_plaintext_1 = self.user_keyring_1.decrypt_key_cipher(key_cipher_1)
        contract_keyring_2.import_contract_key("test_contract", key_plaintext_1)

        with open("./test/integration/fixtures/contract_keyring_test_2/test_contract/contract.key", "rb") as f:
            result = f.read()
        
        self.assertEqual(key_plaintext_1, result, "ContractKeyring.import_contract_key: failed")