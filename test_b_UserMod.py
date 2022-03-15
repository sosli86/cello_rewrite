import unittest
import gnupg
import os
import secrets
import string
import shutil

from cello_mvc.CelloMod import UserMod, ActiveContract
from cello_mvc.CelloDB import CelloDB
from cello_mvc.CelloControl import get_web3


# Init database and model
try:
    shutil.rmtree("test/integration/fixtures/gpg/")
except:
    pass
os.mkdir("test/integration/fixtures/gpg/")
try:
    os.remove("test/integration/fixtures/test_usermod.db")
except:
    pass
db = CelloDB("test/integration/fixtures/test_usermod.db")
db.new_database()
web3 = get_web3()
user_address = web3.eth.accounts[0]
contract_name = "test_contract"
user_name = "test_user"
model = UserMod(db, user_name, web3, user_address, "test/integration/fixtures/gpg/")
active_contract = ActiveContract(web3, contract_name)

## Test essential database functions
# Test init

expected = (f'{user_address}',)
result = db.select_x_from_y_where_z("user_address", "user", f'user_name = ("{user_name}")')[0]
if expected == result:
    print("Init test successful")
else:
    print("Init test unsuccessful")

# test init_user_pub_key

result = model.init_user_pub_key("password")
expected = model.gpg.export_keys(user_name)
if expected == result:
    pub_key = expected
    print("init user pub key test successful")
else:
    print("init user pubkey test unsuccessful")

# test write_contract_to_database

model.write_contract_to_database(contract_name, active_contract.contract_address)
expected = active_contract.contract_address
result = db.select_x_from_y_where_z("contract_address", "contract", "contract_name = ('test_contract')")[0][0]
# if expected == result:
#    print("write_contract_to_database test unsuccessful.")

# test write_new_membership_to_database

contract_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(128))
contract_key_cipher = str(model.gpg.encrypt(contract_key, user_name))
model.write_new_membership_to_database(contract_name, user_name, pub_key, contract_key_cipher)
expected = (f'{user_name}, {contract_name}, {pub_key}, {contract_key_cipher}')
result = model.db.select_x_from_y_where_z("*", "membership")[0]
#if expected == result:
#    print("write new membership to database test successful")
#else:
#    print("write new membership to database test unsuccessful")

# test init contracts from database

model.init_contracts_from_database()
if model.contracts[contract_name].contract_address == active_contract.contract_address:
    print("init contracts from database test successful")
else:
    print("init contracts from database test unsuccessful")

# test populate contract keys from database

model.populate_contract_keys_from_database()
if model.contract_keys[contract_name] == contract_key:
    print("populate contract keys from database successful.")
else:
    print("populate contract keys from database unsuccessful.")



## test basic contract functions

# test add pub key
model.add_pub_key_to_contract(contract_name, pub_key)
## add some receipt stuff to finish the test

# test update pub keys from contract
model.update_pub_keys_from_contract(contract_name)
if len(model.contract_pub_key_logs[contract_name]) > 0:
    print("update pub keys from contract successful")
else:
    print("update pub keys from contract unsuccessful")

# test add key cipher
model.add_key_cipher_to_contract(contract_name, contract_key_cipher)
## blablabla

# test update key ciphers from contract
model.update_key_ciphers_from_contract(contract_name)
#print("update key ciphers from contract succeeded: " + str(model.update_key_ciphers_from_contract(contract_name)))
print(model.contract_key_cipher_logs[contract_name])

# test add message
message = "cello world!"
receipt = model.add_message_to_contract(contract_name, message)
#print(receipt)
## add some stuff based on the receipt to finish your tests

# test update messages from contract
message_update = model.update_messages_from_contract(contract_name)
if len(message_update) > 0:
    print("message update successful.")
#    print("update messages from contract successful.")

else:
    print("update messages from contract unsuccessful.")


## test intermediate database functions

# test update database from message log

model.write_message_logs_to_database(contract_name)