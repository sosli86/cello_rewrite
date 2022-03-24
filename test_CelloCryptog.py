from cello_mvc.CelloCryptog import *
import unittest

class TestKeyFunctions(unittest.TestCase):
    def test_contract_key_gen(self):
        """
        Test that a 32-bit key is generated.
        """
        test_contract_key = contract_key_gen()
        result = len(test_contract_key)
        self.assertIsNotNone(result, "contract_key_gen: nothing!")
    
    def test_encrypt_message(self):
        """
        Test that the encryption function has valid output.
        """
        test_message = "Hello Cello Test"
        test_contract_key = contract_key_gen()
        result = encrypt_message(test_message, test_contract_key)
        self.assertIsNotNone(result, "encrypt_message has no output.")
    
    def test_decrypt_message(self):
        """
        Test that a message can be decrypted.
        """
        test_message = "Hello Cello Test 2"
        test_contract_key = contract_key_gen()
        cryptext = encrypt_message(test_message, test_contract_key)
        result = decrypt_message(cryptext, test_contract_key)
        self.assertEqual(test_message, result, "decrypt_message did not successfully decrypt the test message.")

