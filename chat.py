'''
Author: Eric Zair
File:   chat.py
Description:    This program runs a peer to peer
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
import sys
import threading
import getpass
from elgamal import generatePrivateKey
from elgamal import generateGenerator


#Server thread method
def serverThread(s):
    global session_open
    global username
    print("Enter '/q' to quit chat")
    while True:
        if session_open:
            str = s.recv(100).decode()
            print("\r>>>" + username + str + "\n<<<", end="", flush=True)
            
            #close the connection
            if str == "/q":
                session_open = 0;
                print("Connection closed")
                s.close()
                sys.exit()


#Client thread method.
def clientThread(s):
    global session_open
    while True:
        if session_open:
            str = input("<<< " )
            s.send(str.encode())
            if str == "/q":
                print("Chat termination signal sent!!!")
                session_open = 0;
                s.close()
                sys.exit()


#required globals.
option = int(input("\n(1)Start a session\n(2)Connect to a session\nSelect an option: "))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session_open = 1


#user creates a session. Must wait for another user to join.
if option == 1:
    host = input("Enter your session IP address: ")
    port = int(input("Enter your session port number: "))
    password = getpass.getpass("Enter your session password: ")
    username = input("Enter your session username: ")

    #create the session using given info.
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(2)
    print("Waiting for a client to connect...")

    #start therads
    c, addr = s.accept()
    threading.Thread(target=serverThread, args=(c,)).start()
    threading.Thread(target=clientThread, args=(c,)).start()


#user is connecting to a session. Must enter correct session info.
elif option == 2:
    host = input("Enter session IP: ")
    port = int(input("Enter session Port: "))
    password = getpass.getpass("Enter session password: ")

#attempt to connect to the session
    s.connect((host, port))
    threading.Thread(target=serverThread, args=(s,)).start()
    threading.Thread(target=clientThread, args=(s,)).start()


#user enterd a non existing option
else:
    print("Incorrect option")
    sys.exit()