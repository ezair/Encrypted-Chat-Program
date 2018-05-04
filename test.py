import sys
import socket
import hashlib
import pyaes
from threading import Thread
from getpass import getpass
from os import system
from Elgamal import generatePrivateKey, generateGenerator, generateRandomPrime

p = generateRandomPrime(128)
a = generatePrivateKey(128)
b = generatePrivateKey(128)
g = generateGenerator(p)
gab = pow(g, a*b, p) >> 16
print(gab)
keys = hashlib.sha256(str(gab).encode('utf-8')).digest()
key = keys[:16]
AES = pyaes.AESModeOfOperationCTR(key)

msg = 'hello world, i am eric'.encode('utf-8')
print("This is the message:", msg)

encrypted_msg = AES.encrypt(msg)
print("This is the encrypted message:", encrypted_msg)
print(encrypted_msg)

AES = pyaes.AESModeOfOperationCTR(key)
decrypted_msg = AES.decrypt(encrypted_msg)
print("This is the decrypted message:", decrypted_msg.decode('windows-1252'))
#________________________new test