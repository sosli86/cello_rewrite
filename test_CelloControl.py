from cello_mvc.CelloControl import CelloControl, get_web3
from cello_mvc.CelloMod import UserMod
from cello_mvc.CelloDB import CelloDB
from threading import *
import os
import time

web3 = get_web3()

user_name = "test_user"
user_address = web3.eth.accounts[0]

contract_name = "test_contract"

dbpath = "cellocontrol_test.db"

try:
    os.remove(dbpath)
except:
    pass

db = CelloDB(dbpath)
db.new_database()


model = UserMod()
model.set_db(db)
model.new_user(user_name, user_address, "some password")

control = CelloControl()
control.set_model(model)
control.set_username(user_name)
control.set_web3(web3)


contract_key = control.contract_key_gen()
contract_key_cipher = control.encrypt_contract_key(contract_key)

control.open_contract(contract_name)
model.set_contract_key(contract_name, contract_key)

control.add_new_message(contract_name, "first message.")

control.update_messages()

test_archive = model.contract_message_archives[contract_name]

print("first archive: " + str(test_archive))

control.add_new_message(contract_name, "second message.")

control.update_messages()

test_archive = model.contract_message_archives[contract_name]

print("second archive: " + str(test_archive))

control.add_new_message(contract_name, "third message.")

control.update_messages()

test_archive = model.contract_message_archives[contract_name]

print("third archive: " + str(test_archive))




