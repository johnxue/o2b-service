# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import base64
from binascii import b2a_hex, a2b_hex

PADDING = '\0'

pad_it = lambda s: s+(16 - len(s)%16)*PADDING  
key = '49c30f5f769a6e2faf4e1ca0cd23679c'
iv = 'aG5sGA?$Qv#u$6)h'
iv='T45WdixNSdZUkmby'

source = 'johnxue@163.com '
generator = AES.new(key, AES.MODE_CBC, iv)
crypt = generator.encrypt(pad_it(source))   
print(pad_it(source))

print(crypt)

cryptedStr = base64.b64encode(crypt)
print("\nStr=%s\n"%cryptedStr)
print("\n")
print(base64.b64decode(cryptedStr))

print("[%d]" % len(cryptedStr))
generator = AES.new(key, AES.MODE_CBC, iv)

cryptedStr='CRyrxKZmIaYEaWBnZqJxYw2wDAKC7mI9eRqlffmdob0='
cryptedStr='qg0s/BMzYfO+opRFfxdmbnYl3QK4Xer/ZswQFBu/pmo='
crypt=base64.b64decode(cryptedStr)


recovery = generator.decrypt(crypt).decode()
print(recovery.rstrip(PADDING))
print(recovery)

#print(base64.b64decode('YWRtaW46YWRtaW4='))
