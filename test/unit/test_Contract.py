import unittest
from cello_mvc.Contract import Contract, compile_source_file, deploy_contract
from cello_mvc.CelloControl import get_web3

class TestContract(unittest.TestCase):
    def setUp(self):
        self.web3 = get_web3()
        self.contract_name = "test_contract"
        self.contract = Contract("cello_mvc/Contact.sol", self.web3)
    
    def test_init(self):
        contract_address = self.contract.contract_address
        self.assertIsNotNone(contract_address)

    def test_get_number_of_messages(self):
        expected = 0
        result = self.contract.get_number_of_messages()
        self.assertEqual(expected, result, "Could not get number of messages = 0")

    def test_add_message(self):
        self.contract.add_message("test_message")
        result = self.contract.get_number_of_messages()
        expected = 1
        self.assertEqual(expected, result, "Message not added.")
    
    def test_get_message_by_number(self):
        expected = "test_message_number_2"
        self.contract.add_message(expected)
        n = self.contract.get_number_of_messages()
        result = self.contract.get_message_by_number(n-1)
        self.assertEqual(expected, result, "Could not get test message by number.")