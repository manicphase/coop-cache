from hashlib import sha256 as SHA256
import M2Crypto
import os

class CreateUser():
    def __init__(self, username, password=None):
        self.key = M2Crypto.RSA.gen_key(1024, 65537)
        try:
            os.mkdir("local_keys")
        except:
            pass
        self.key.save_key("local_keys/"+username+'-private.pem', None)
        self.key.save_pub_key("local_keys/"+username+"-public.pem")
        print("new key generated")
        
class CryptoStuff():
    def __init__(self, username):
        M2Crypto.Rand.rand_seed(os.urandom(1024))
        self.key = M2Crypto.EVP.load_key(username+'-private.pem')
        print("loaded key from file")
        with open(username+"-public.pem") as f:
            self.pub_key = f.read()            
            
    def public_key(self):
        return self.pub_key
            
    def sign(self, message):
        self.key.reset_context(md="sha256")
        self.key.sign_init()
        self.key.sign_update(message)
        signature = self.key.sign_final()
        return signature.encode("base64")
        
    def send_public(self, message):
        checksum = SHA256(message).hexdigest()
        return checksum, self.sign(checksum)
        
    def verify_public(self, message, signature, sender_key):
        bio = M2Crypto.BIO.MemoryBuffer(sender_key)
        rsa = M2Crypto.RSA.load_pub_key_bio(bio)
        pubkey = M2Crypto.EVP.PKey()
        pubkey.assign_rsa(rsa)
        pubkey.reset_context(md="sha256")
        pubkey.verify_init()
        pubkey.verify_update(message)
        return pubkey.verify_final(signature.decode("base64")) == 1
        
if __name__ == "__main__":
    cs = CryptoStuff()
    checksum, signature = cs.send_public("i am also message")
    wrong_checksum, wrong_signature = cs.send_public("i am wrong message")

    pub_key = cs.public_key()

    print("checksum: " + checksum)
    print("signature: " + signature)

    print(cs.verify_public(checksum, signature, pub_key))
