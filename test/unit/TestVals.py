from ..cello_mvc.CelloDB import CelloDB
from ..cello_mvc.CelloControl import get_web3
from ..cello_mvc.CelloMod import UserMod, ActiveContract
from ..cello_mvc.Contract import Contract

def TestVals():
    TestVals = {}
    web3 = get_web3()
    db = CelloDB()
    TestVals["web3"] = web3
    TestVals["user_name"] = "test"
    TestVals["user_address"] = web3.eth.accounts[0]
    TestVals["contract_name"] = "test_contract"
    TestVals["db"] = db
    return TestVals