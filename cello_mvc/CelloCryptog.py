from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
from os.path import exists
import binascii
import string
import secrets
import base64
import os
import glob

class ContractKeyring:
    def __init__(self, keyring_path):
        if not exists(keyring_path):
            os.mkdir(keyring_path)
        self.keyring_path = keyring_path

    # symmetric key functions
    def contract_key_gen(self, contract_name: str):
        os.mkdir(self.keyring_path + f'/{contract_name}')
        random_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(32))
        random_key_bytes = random_key.encode('ascii')
        contract_key = base64.b64encode(random_key_bytes)
        contract_key_file = open(self.keyring_path + f'/{contract_name}/contract.key', "wb")
        contract_key_file.write(contract_key)
        contract_key_file.close()
    
    def import_contract_key(self, contract_name: str, contract_key: bytes):
        if not exists(self.keyring_path + f'/{contract_name}'):
            os.mkdir(self.keyring_path + f'/{contract_name}')
        contract_key_file = open(self.keyring_path + f'/{contract_name}/contract.key', "wb")
        contract_key_file.write(contract_key)
        contract_key_file.close()
    
    def get_contract_key(self, contract_name: str):
        with open(self.keyring_path + f'/{contract_name}/contract.key', "rb") as f:
            contract_key = f.read()
        return contract_key

    def encrypt_message(self, message: str, contract_name: str):
        contract_key = self.load_contract_key(contract_name)
        key = Fernet(contract_key)
        message_cipher = key.encrypt(bytes(message, encoding='utf-8'))
        return message_cipher

    def decrypt_message(self, message_cipher: bytes, contract_name: str):
        contract_key = self.load_contract_key(contract_name)
        key = Fernet(contract_key)
        message = key.decrypt(message_cipher)
        message_output = message.decode("utf-8")
        return message_output
    
    def list_contracts(self):
        contract_list = os.listdir(self.keyring_path)
        return contract_list
    
    # asymmetric key functions
    def import_user_key(self, contract_name: str, new_public_key: str):
        packed_pem_string = new_public_key.split(":::::")
        pem_lines = packed_pem_string[1].split("+-+-+")[0:-1]
        pem = "-----BEGIN PUBLIC KEY-----\n"
        for line in pem_lines:
            pem += line + "\n"
        pem += "-----END PUBLIC KEY-----"

        new_user_name = packed_pem_string[0]
        new_pub_key = pem
        if not exists(f'{self.keyring_path}/{contract_name}/{new_user_name}.pem'):
            with open(f'{self.keyring_path}/{contract_name}/{new_user_name}.pem', "w") as f:
                f.write(new_pub_key)
    
    def open_public_key(self, user_name: str, contract_name: str):
        with open(f'{self.keyring_path}/{contract_name}/{user_name}.pem', "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        return public_key
    
    def encrypt_contract_key(self, contract_name: str, user_name: str):
        public_key = self.open_public_key(user_name, contract_name)
        with open(self.keyring_path + f'/{contract_name}/contract.key', 'rb') as f:
            encrypted = public_key.encrypt(
                f.read(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        with open(self.keyring_path + f'/{contract_name}/{user_name}.cyph', "wb") as f:
            f.write(binascii.b2a_hex(encrypted))
        return encrypted
    
    def decrypt_contract_key(self, contract_name: str, contract_key_cipher: str):
#        contract_key_cipher = binascii.a2b_base64(contract_key_cipher)
        contract_key = self.private_key.decrypt(
            contract_key_cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        with open(self.keyring_path + f'/{contract_name}/contract.key', "wb") as f:
            f.write(contract_key)
        return contract_key
    
    def list_authenticated_contract_members(self, contract_name: str):
        member_list = []
        for member_key in glob.glob(self.keyring_path + f'/{contract_name}/*.cyph'):
            member_list.append(member_key.split(".cyph")[0])
        return member_list
    
    def list_unauthenticated_contract_members(self, contract_name: str):
        member_list = []
        for member_key in glob.glob(self.keyring_path + f'/{contract_name}/*.pem'):
            member_list.append(member_key.split(".pem")[0].split("/")[-1])
        return member_list
    
    # state monitoring
    def get_user_key_state(self, contract_name: str):
        number_of_user_keys = len(self.list_authenticated_contract_members(contract_name))
        return number_of_user_keys
    
    def get_key_cipher_state(self, contract_name: str):
        number_of_key_ciphers = len(self.list_unauthenticated_contract_members(contract_name))
        return number_of_key_ciphers

class CelloKeyring:
    def __init__(self, keyring_path):
        self.keyring_path = keyring_path
        if not exists(keyring_path):
            os.mkdir(keyring_path)
    
    def set_user_name(self, user_name: str):
        self.user_name = user_name

    def generate_keypair(self):
        if not exists(f'{self.keyring_path}/private_key.pem') and not exists(f'{self.keyring_path}/public_key.pem'):
            
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            pem_priv = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(f'{self.keyring_path}/private_key.pem', 'wb') as f:
                f.write(pem_priv)

            self.public_key = self.private_key.public_key()
            pem_pub = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            with open(f'{self.keyring_path}/public_key.pem', 'wb') as f:
                f.write(pem_pub)
        else:
            self.open_keypair()
            pem_pub = self.public_key
            pem_priv = self.private_key
    
    def pack_pubkey(self):
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pem = pem.decode()
        pem = pem.split("\n")[1:-2]
        output_pem = f'{self.user_name}:::::'
        for line in pem:
            output_pem+=line + "+-+-+"
        return output_pem
    
    def open_keypair(self):
        with open(f'{self.keyring_path}/private_key.pem', "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        with open(f'{self.keyring_path}/public_key.pem', "rb") as key_file:
            self.public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    def decrypt_key_cipher(self, key_cipher: bytes):
        contract_key = self.private_key.decrypt(
            key_cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return contract_key