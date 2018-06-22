'''
Author: Eric Zair
File:   chat.py
Description:    This program runs a peer to peer
                two person encrypted chat program.
                Keys are generated with elgamal public 
                key encryption from the Elgamal module
		located in this floder.
                Encryption is done with AES encryption
                from the pyaes library.

                Dependencies:
                    python3
                    Elgamal.py
                    pyaes (deb file can be found online.)
                    pygame Library (sudo pip install pygame) make sure it is python3 pygame.
'''
import time
import sys
import socket
import hashlib
import pyaes
from threading import Thread
from getpass import getpass
from os import system
from Elgamal import generatePrivateKey, generateGenerator, generateRandomPrime
from pygame import mixer


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


#play a sound when user receives a message
#parameters:
#           string path_to_sound(...path to the sound file)
#return type: void
def playReceiveSound(path_to_sound):
    mixer.init()
    mixer.music.load(path_to_sound)
    mixer.music.play()


#send keys from the client to the server.
#these keys are formated as a string so that
#they can be sent over a socket connection.
#The client will have to take the keys as a string and split them
#then type cast them back into integers.
#parameters: socket s(the socket that you the server are hosting)
#return type: void 
#			  string keys(the keys in the following form "g ga p")
def sendKeysToClient(s):
	global a
	global p
	
    #generate all keys.
	p = generateRandomPrime(128)
	a = generatePrivateKey(128)
	g = generateGenerator(p)
	ga = pow(g, a, p)

	#send the keys to the client
	keys = str(g) + " " + str(ga) + " " + str(p)
	try:
		s.send(keys.encode())
	except socket.error as e:
		print("Failed to send keys to the client.")


#take the string passed in(keys_as_string) as a parameter
#and split it into the keys it holds.
#the string is in the form "g ga p"
#After getting the individual keys, we now generate b and g^b
#we then send g^b to the server. Then we have completed our key exchange.
#after this we can being sending encrypted messages to one another.
#parameters:
#			s socket(The socket of the server you are sending keys to)
#			string keys_as_string(the keys that the Server sends the clients)
#						this is in the form "g ga p"
#return type: void
def sendKeysToServer(s, keys_as_string):
    global gab
    global p
    keys = keys_as_string.split(" ")
    p = int(keys[2])
    ga = int(keys[1])
    g = int(keys[0])
    b = generatePrivateKey(128)
    gb = pow(g, b, p)
    gab = pow(ga, b, p)
    s.send(str(gb).encode())


#Thread used for receiving messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void
def receiveMsg(s, username):
    global session_open
    global gab
    
    #Send keys to server from client
    if username.endswith("] "):
    	keys_as_string = s.recv(4096).decode()
    	sendKeysToServer(s, keys_as_string)
    #Send keys to client from server
    else:
    	gb = int(s.recv(4096).decode())
    	gab = pow(gb, a, p)
    
    system("clear")
    print("*Enter '/quit' to exit chat*")
    #Start the encrypted chat
    while True:
        key = hashlib.sha256(str(gab).encode()).digest()
        #Receive the Encrypted message and decrypt.
        if session_open:
            msg = s.recv(4096)
            decrypted_msg = pyaes.AESModeOfOperationCTR(key).decrypt(msg).decode()
            
            #print out decrypted message.
            if not decrypted_msg.endswith("> ") and not decrypted_msg.endswith("] "):
                playReceiveSound("../sounds/received.mp3")
                print("\r\r" + decrypted_msg + "\n", end="", flush=True)           
                #close the connection
                if decrypted_msg.endswith(" /quit"):
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
    global gab

    #Send the keys to client before messages start.
    if username.endswith("> "):
        sendKeysToClient(s)

   #...cuz globals are dumb...this is required.
    while gab == 0:
        time.sleep(1)

    while True:
        key = hashlib.sha256(str(gab).encode()).digest()
	   #retrieve message here.
        if session_open:
            #create and send encrypted message.
            msg = username + input(username) 
            encrypted_msg = pyaes.AESModeOfOperationCTR(key).encrypt(msg)
            if msg.endswith(" /quit"):
                closeConnection(s)
            else:
                s.send(encrypted_msg)
        #close connection
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

    #create the session using given info.
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
    #unable to host a connection
    except socket.error as e:
        print("Unable to set up a connection on IP address:", host, "port number", port)
        s.close()
        sys.exit()

    #username cannot be an < 5 chars long.
    #make username first letter capital automatically.
    username = ""
    while len(username) < 5:
        username = input("Enter your session username(must be at least 5): ").rstrip(" ")
    username = "[" + username[0].upper() + username[1 : ] + "] "

    #client connects.
    print("\nWaiting for a to connect...")  
    print("The IP to connect to is:", host)
    print("The Port to connect to is:", port)
    c, addr = s.accept()
    #Sending and receiving up and running.
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

    #attempt to connect.
    try:
        s.connect((host, port))
    except socket.error as e:
        print('Information must be Incorrect. There is no host "' + str(host) + "' with port '" + str(port) + "'")
        sys.exit()

    #username cannot be an < 5 chars long.
    #make username first letter capital automatically.
    username = ""
    while len(username) < 5:
        username = input("Enter your session username(must be at least 5 characters): ").rstrip(" ")
    username = "<" + username[0].upper() + username[1 : ] + "> "

    #start threads if connected.
    Thread(target=receiveMsg, args=(s, username)).start()
    Thread(target=sendMsg, args=(s, username)).start()


#_____________________________________________________________________________________
#int used as a boolean to determine if chat is still open
session_open = 1
#The global variables below are used to hold the values of certain keys.
#Threads cannot store variable and communicate between one another.
#This is a cheap fix for that issue.
gab = 0
a = 0
p = 0
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
	    print("Incorrect option.")
	    sys.exit()

if __name__ == '__main__':
	main()
