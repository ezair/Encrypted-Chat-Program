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
                    Elgamal.py
                    pycrypto library (sudo apt-get install pycrypto)
                    AES.py
'''
import sys
import socket
import AES
from threading import Thread
from getpass import getpass
from os import system
from Elgamal import generatePrivateKey, generateGenerator, generateRandomPrime


#close the connection on server.
#parameters:
#			socket s(socket that the server is on)
#return type: void
def closeConnection(s):
    global session_open
    system("clear")
    print("Connection closed.")
    session_open = 0
    s.close()
    sys.exit()


#Thread used for receiving messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void 
def receiveMsg(s, username):
    global session_open
    print("*Enter '/quit' to exit chat*")
    while True:
        #Receive the message here
        if session_open:
            msg = s.recv(100).decode()
            #if the message is blank we don't print it
            if not msg.endswith("> "):
                print("\r\r" + msg + "\n", end="", flush=True)            
            #close the connection
            if msg.endswith(" /quit"):
                closeConnection(s)
        #close
        else:
            closeConnection(s)


#Thread used for sending messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void 
def sendMsg(s, username):
    global session_open

    '''
    #grab keys from the other user.
    #now, we can form g to the gab and save it.
    #string is formated as "g g^key p" with spaces between.
    keys = s.recv(100).decode().split(" ")
    gab = pow(keys[1], b)
    '''
    while True:
    	#retrieve message here.
        if session_open:
            msg = username + input(username)
            s.send(msg.encode())
            #close connection if "/quit" as input
            if msg.endswith(" /quit"):
                closeConnection(s)
        #close
        else:
        	closeConnection(s)


#Create a session (as a server) and wait for a client to connect.
#Once a client successfully connects, computers begin to chat.
#paramaters:
#			socket s (used to host connection)
#return type: void
def startSession(s):
    host = input("Enter your session IP address: ")
    port = int(input("Enter your session port number: "))
    password = getpass("Enter your session password: ")
    username =  "<" + input("Enter your session username: ") + "> "
    
    #create the session using given info.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Waiting for a client to connect...")

    '''
    #create keys and send them to client as a tuple
    p = generateRandomPrime(256)
    a = generatePrivateKey(256)
    g = generateGenerator(p)
    ga = pow(g, a, p)
    keys = str(g) + " " + str(ga), + " " + str(p)
    '''

    #start therads
    c, addr = s.accept()
    Thread(target=receiveMsg, args=(c, username)).start()
    Thread(target=sendMsg, args=(c, username)).start()


#Join a session (as a client)
#Once successfully connected, computers begin to chat
#paramaters:
#			socket s (used to join connection)
#return type: void
def connectToSession(s):    
    host = input("Enter session IP: ")
    port = int(input("Enter session Port: "))
    password = getpass("Enter session password: ")
    username = "<" + input("Enter your session name: ") + "> " 
    s.connect((host, port))

    #start threads
    Thread(target=receiveMsg, args=(s, username)).start()
    Thread(target=sendMsg, args=(s, username)).start()

#_____________________________________________________________________________________
#int used as a boolean to determine if chat is still open
session_open = 1
#______________________________________________________________________________________
def main():
	option = int(input("\n(1)Start a session\n(2)Connect to a session\nSelect an option: "))
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#user creates a session. 
	#Must wait for another user to join.
	if option == 1:
	    startSession(s)

	#user is connecting to a session.
	#Must enter correct session info.
	elif option == 2:
	    connectToSession(s)

	#user entered a non-existent option
	else:
	    print("Incorrect option")
	    sys.exit()

if __name__ == '__main__':
	main()