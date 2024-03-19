import rsa, pickle, os
from Scripts.logger import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

logger.info('RealDL Encryption Module : RSA')

class RSA_Keys:
    def __init__(self, bits):
        self.bits = bits
        key_dir = "../Keys" if os.path.exists("../Keys") else "Keys"
        public_key_path = os.path.join(key_dir, "public.pem")
        private_key_path = os.path.join(key_dir, "private.pem")

        try:
            with open(public_key_path, "rb") as f:
                self.public_key = rsa.PublicKey.load_pkcs1(f.read())

            with open(private_key_path, "rb") as f:
                self.private_key = rsa.PrivateKey.load_pkcs1(f.read())
        except FileNotFoundError:
            self.public_key, self.private_key = rsa.newkeys(self.bits)
            with open(public_key_path, "wb") as f:
                f.write(self.public_key.save_pkcs1("PEM"))

            with open(private_key_path, "wb") as f:
                f.write(self.private_key.save_pkcs1("PEM"))

    def export_keys(self):
        return self.public_key, self.private_key
    
class RSA_Encryption:
    def __init__(self, public_key):
        try:
            self.public_key = public_key
        except ValueError as e:
            logging.error(f"Error: {e}")

    def encrypt(self, message):
        try:
            return rsa.encrypt(self.serialise(message), self.public_key)
        except ValueError as e:
            logging.error(f"Error: {e}")
    
    def decrypt(self, encrypted_message, private_key):
        try:
            encoded_message = rsa.decrypt(encrypted_message, private_key)
            return self.unserialise(encoded_message)
        except ValueError as e:
            logging.error(f"Error: {e}")

    def serialise(self, data):
        try:
            return pickle.dumps(data) 
        except ValueError as e:
            logging.error(f"Error: {e}")

    def unserialise(self, data):
        try:
            return pickle.loads(data)
        except ValueError as e:
            logging.error(f"Error: {e}")

class AES_Keys:
    def __init__(self, bits):
        self.bytes = bits // 8
        self.key = get_random_bytes(self.bytes)

    def export_key(self):
        return self.key
    
class AES_Encryption:
    def __init__(self, key):
        try:
            self.key = key
            self.cipher = AES.new(self.key, AES.MODE_ECB)
        except ValueError as e:
            logging.error(f"Error: {e}")

    def encrypt(self, message):
        try:
            message_bytes = self.serialise(message)
            padded_message = pad(message_bytes, AES.block_size)
            return self.cipher.encrypt(padded_message)
        except ValueError as e:
                logging.error(f"Error: {e}")
    
    def decrypt(self, encrypted_message):
        try:
            decrypted_padded_message = self.cipher.decrypt(encrypted_message)
            decrypted_unpadded_bytes_message = unpad(decrypted_padded_message, AES.block_size)
            return self.unserialise(decrypted_unpadded_bytes_message)
        except ValueError as e:
            logging.error(f"Error: {e}")

    def serialise(self, data):
        try:
            return pickle.dumps(data) 
        except ValueError as e:
            logging.error(f"Error: {e}")

    def unserialise(self, data):
        try:
            return pickle.loads(data)
        except ValueError as e:
            logging.error(f"Error: {e}")
