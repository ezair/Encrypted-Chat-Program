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
from os import system
from elgamal import generatePrivateKey
from elgamal import generateGenerator


#Thread used for receiving messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void 
def receiveMsg(s):
    global session_open
    global username
    print("*Enter '/quit' to exit chat*")
    while True:
        #Receive the message here
        if session_open:
            str = s.recv(100).decode()

            #if the message is blank we don't bother printing it
            if not str.endswith("> "):
                print("\r\r" + str + "\n", end="", flush=True)
            
            #close the connection
            if str.endswith(" /quit"):
                session_open = 0;
                system("clear")
                print("Connection closed.")
                s.close()
                sys.exit()
        else:
            system("clear")
            print("Connection closed.")
            s.close()
            sys.exit()


#Thread used for sending messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void 
def sendMsg(s):
    global session_open
    global username
    while True:
        if session_open:
            str = username + input(username)
            s.send(str.encode())

            #close connection in the even that user enters /q command
            if str.endswith("/quit"):
                system("clear")
                print("Connection closed.")
                session_open = 0;
                s.close()
                sys.exit()
        else:
            system("clear")
            print("Connection closed.")
            s.close()
            sys.exit()


#required global vairables.
option = int(input("\n(1)Start a session\n(2)Connect to a session\nSelect an option: "))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session_open = 1

#_______________________________________________________________________________________

#user creates a session. 
#Must wait for another user to join.
if option == 1:
    host = input("Enter your session IP address: ")
    port = int(input("Enter your session port number: "))
    password = getpass.getpass("Enter your session password: ")
    username =  "<" + input("Enter your session username: ") + "> "

    #create the session using given info.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Waiting for a client to connect...")

    #start therads
    c, addr = s.accept()
    threading.Thread(target=receiveMsg, args=(c,)).start()
    threading.Thread(target=sendMsg, args=(c,)).start()


#user is connecting to a session.
#Must enter correct session info.
elif option == 2:
    host = input("Enter session IP: ")
    port = int(input("Enter session Port: "))
    password = getpass.getpass("Enter session password: ")
    username = "<" + input("Enter your session name: ") + "> "

#attempt to connect to the session
    s.connect((host, port))
    threading.Thread(target=receiveMsg, args=(s,)).start()
    threading.Thread(target=sendMsg, args=(s,)).start()


#user entered a non-existent option
else:
    print("Incorrect option")
    sys.exit()