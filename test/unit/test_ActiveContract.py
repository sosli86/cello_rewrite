from cello_mvc.Contract import Contract
from cello_mvc.CelloMod import ActiveContract
from cello_mvc.CelloControl import get_web3

import unittest

class TestContract(unittest.TestCase):
    def setUp(self):
        self.web3 = get_web3()
        self.contract_name = "test_contract"
        self.active_contract = ActiveContract(self.web3, self.contract_name)
        self.contract_address = self.active_contract.contract_address
    
    def test_init(self):
        new_contract_instance = ActiveContract(self.web3, self.contract_name, self.contract_address)
        contract_address = new_contract_instance.contract_address
        self.assertEqual(self.contract_address, contract_address, "Could not re-instantiate active contract.")
    
    def test_add_message(self):
        expected = 1
        result = self.active_contract.add_message("test_message")
        self.assertEqual(expected, result, "Could not add message")
    
    def test_get_all_messages(self):
        self.active_contract.add_message("test_message")
        expected = "test_message"
        result = self.active_contract.get_all_new_messages(0)[0]
        self.assertEqual(expected, result, "Could not get all messages.")