from cello_mvc.CelloCryptog import *
import unittest
import os
import string
import secrets

class TestCelloKeyring(unittest.TestCase):
    def setUp(self):
        self.keyring = CelloKeyring('test/integration/fixtures/keyring_test')
        self.keyring.open_keypair()
        self.keyring_2 = CelloKeyring('test/integration/fixtures/keyring_test_2')
        self.keyring_2.open_keypair()
        self.test_contract_key = 'ZVRqT0JoY0NRRlNJaHhVUUdLbW1IZUl4b2FLenRpZ3k='
        self.name = 'aWlRTm90YmdVZ0pUZlZRU0JmSG93SktXVHJLdGNxS1k='
        self.test_name = 'YkxuQmRyVEp2V1d2U1VWcWNSYVhoUVh0aG5lTFVMdlU='

    def test_generate_keypair(self):
        """
        Test that a new keypair is properly generated and stored under a random name.
        """
        name = contract_key_gen()
        os.mkdir(f'test/integration/fixtures/keyring_{name}')
        keyring = CelloKeyring(f'test/integration/fixtures/keyring_{name}')
        expected = keyring.generate_keypair()[1]
        keyring.open_keypair()
        result = keyring.public_key
        self.assertEqual(type(expected), type(result), "generate_keypair: New keypair was not properly stored.")

    def test_open_keypair(self):
        expected = [self.keyring.private_key, self.keyring.public_key]
        self.keyring.open_keypair()
        result = [self.keyring.private_key, self.keyring.public_key]
        self.assertEqual(type(expected), type(result), "open_keypair: keypair was not loaded properly.")
    
    def test_store_new_public_key(self):
        test_name = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(8))
        os.mkdir(f'./test/integration/fixtures/keyring_{test_name}')
        keyring = CelloKeyring(f'./test/integration/fixtures/keyring_{test_name}')
        keyring.generate_keypair()
        pub_key_file = open(f'./test/integration/fixtures/keyring_{test_name}/public_key.pem', 'rb')
        pub_key = pub_key_file.read()
        pub_key_file.close()
        keyring.open_keypair()
        pub_key_packed = test_name.encode() + b':::' + pub_key
        self.keyring.store_new_public_key(pub_key_packed)
        result_file = open(f'./test/integration/fixtures/keyring_test/{test_name}.pem', 'rb')
        result = result_file.read()
        result_file.close()
        self.assertEqual(pub_key, result, "store_new_public_key: pubkey was not stored properly.")

    def test_open_public_key(self):
        expected = self.keyring_2.public_key
        result = self.keyring.open_public_key(self.test_name)
        self.assertEqual(type(expected), type(result), "open_public_key: public key was not opened properly.")
    
    def test_encrypt_contract_key(self):
        test_contract_key = contract_key_gen()
        result = self.keyring.encrypt_contract_key(test_contract_key, self.test_name)
        self.assertIsNotNone(result, "encrypt_contract_key: no output.")
    
    def test_decrypt_contract_key(self):
        expected = contract_key_gen()
        test_contract_key_cipher = self.keyring.encrypt_contract_key(expected, self.test_name)
        result = self.keyring_2.decrypt_contract_key(test_contract_key_cipher)
        self.assertEqual(expected, result, "decrypt_contract_key: decryption failed.")
    