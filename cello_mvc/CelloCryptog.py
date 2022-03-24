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

def contract_key_gen():
    random_key = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(32))
    random_key_bytes = random_key.encode('ascii')
    contract_key = base64.b64encode(random_key_bytes)
    return contract_key

def encrypt_message(message, contract_key):
    contract_key = contract_key
    key = Fernet(contract_key)
    message_cipher = key.encrypt(bytes(message, encoding='utf-8'))
    return message_cipher

def decrypt_message(message_cipher, contract_key):
    key = Fernet(contract_key)
    message = key.decrypt(message_cipher)
    return message.decode("utf-8")


class CelloKeyring:
    def __init__(self, keyring_path):
        self.keyring_path = keyring_path

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
        return [self.private_key, self.public_key]
    
    def pack_pubkey(self):
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pem = pem.decode()
        pem = pem.split("\n")[1:-2]
        output_pem = ""
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
    
    def store_new_public_key(self, new_public_key):
        packed_pem_string = new_public_key.split(":::")
        pem_lines = packed_pem_string[1].split("+-+-+")[0:-1]
        pem = "-----BEGIN PUBLIC KEY-----\n"
        for line in pem_lines:
            pem += line + "\n"
        pem += "-----END PUBLIC KEY-----"

        new_user_name = packed_pem_string[0]
        new_pub_key = pem
        if not exists(f'{self.keyring_path}/{new_user_name}.pem'):
            with open(f'{self.keyring_path}/{new_user_name}.pem', "w") as f:
                f.write(new_pub_key)
    
    def open_public_key(self, user_name):
        with open(f'{self.keyring_path}/{user_name}.pem', "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        return public_key
    
    def encrypt_contract_key(self, contract_key, user_name=""):
        if user_name != "":
            public_key = self.open_public_key(user_name)
        else:
            public_key = self.public_key
        encrypted = public_key.encrypt(
            contract_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return binascii.b2a_hex(encrypted).decode()
    
    def decrypt_contract_key(self, contract_key_cipher):
        contract_key_cipher = binascii.a2b_hex(contract_key_cipher)
        try:
            contract_key = self.private_key.decrypt(
                contract_key_cipher,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except:
            pass
        return contract_key.encode()

if __name__ == "__main__":
    keyring = CelloKeyring(".")
    keyring.generate_keypair()
    sample_contract_key = contract_key_gen()
    print("Unencrypted sample contract key: " + sample_contract_key)
    sample_contract_key_cipher = keyring.encrypt_contract_key(sample_contract_key)
    print("Encrypted sample contract key: " + str(sample_contract_key_cipher))
    decrypted_sample_contract_key = keyring.decrypt_contract_key(sample_contract_key_cipher)
    print("Decrypted sample contract key: " + decrypted_sample_contract_key)