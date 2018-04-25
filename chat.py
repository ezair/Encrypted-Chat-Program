'''
Author:	Eric Zair
File:	chat.py
Description:	This program runs a peer to peer
				two person encrypted chat program.
				Keys are generated with elgamal public 
				key encryption.
				Encryption is done with AES encryption
				from the pycrypto language.

				Dependencies:
					python3
					elgamal.py
					pycrypto library
					aes.py
'''
import socket
import time
from elgamal import generatePrivateKey
from elgamal import generateGenerator