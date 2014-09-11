from Crypto.Cipher import AES
from Crypto import Random
import base64

class AESCipher:
    def __init__(self, key):
        BS = 16
        self.pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        self.unpad = lambda s : s[0:-ord(s[-1])]
        self.key = self.pad(key[0:16])
        self.key=key
        pass

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = "1011121314151617"
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        #enc = enc.replace(' ', '+')
        #enc = base64.b64decode(enc)
        #iv = enc[:16]
        iv = "1011121314151617"
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        #return self.unpad(cipher.decrypt( en[c16:]))
        return self.unpad(cipher.decrypt(enc))
    

def main():     

    cipher = AESCipher('49c30f5f769a6e2faf4e1ca0cd23679c')
   # encrypteddata =cipher.encrypt('MTAxMTEyMTMxNDE1MTYxN2hpOWxqQ1ozS0ZGdWRtZ0szU2UrYXc9PQ==        ')
   # print(encrypteddata)         

    decryptdata =cipher.decrypt('MTAxMTEyMTMxNDE1MTYxN2hpOWxqQ1ozS0ZGdWRtZ0szU2UrYXc9PQ==        ')
    print(decryptdata)

main()
