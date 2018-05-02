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


#send keys from the client to the server.
#these keys are formated as a string so that
#they can be sent over a socket connection.
#The client will have to take the keys as a string and split them
#then type cast them back into integers.
#parameters: socket s(the socket that you the server are hosting)
#return type: void 
#			  string keys(the keys in the following form "g ga p")
def sendKeysToClient(s):
	global ga
	p = generateRandomPrime(128)
	#proble occuring right here.
	#even though is of type int.
	a = generatePrivateKey(128)
	g = generateGenerator(p)
	ga = pow(g, a, p)
	#Shift right in order to make the keys 
	keys = str(g) + " " + str(ga) + " " + str(p)

	#send the keys to the client
	try:
		s.send(keys.encode())
	except socket.error as e:
		print("Failed to send key to client.")


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
	keys = keys_as_string.split(" ")
	p = int(keys[2])
	ga = int(keys[1])
	g = int(keys[0])
	b = generatePrivateKey(128)
	gb = pow(g, b, p)
	gab = pow(gb, a, p) >> 128
	s.send(str(gb).encode())
	print("Sending keys to server")

#Thread used for receiving messages.
#paramaters: 
#           socket s(socket that the client connects to)
#return type: void
def receiveMsg(s, username):
    global session_open

    #get the keys back from the client.
    #then send your version of the keys right back to it.
    keys_as_string = s.recv(128).decode()
    #print(keys_as_string)
    #sendKeysToServer(s, keys_as_string)

    print("*Enter '/quit' to exit chat*")
    while True:
        #Receive the message here
        if session_open:
            msg = s.recv(128).decode()
            #if the message is blank we don't print it
            if not msg.endswith("> ") or not msg.endswith("] "):
                #print("\r\r" + msg + "\n", end="", flush=True)            
            	pass
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
    
    #Basically, if this thread is the server thread,
    #you are going to want to send the keys to the client
    if username.endswith("] "):
    	sendKeysToClient(s)
    
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
    host = "127.0.0.1"
    port = 8080
    #host = input("Enter your session IP address: ")
    #port = int(input("Enter your session port number: "))
    password = getpass("Enter your session password: ")
    username =  "<" + input("Enter your session username: ") + "> "
    
    #create the session using given info.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Waiting for a to connect...")
    
    #client connects.
    c, addr = s.accept()
    Thread(target=receiveMsg, args=(c, username)).start()
    Thread(target=sendMsg, args=(c, username)).start()

#Join a session (as a client)
#Once successfully connected, computers begin to chat
#paramaters:
#			socket s (used to join connection)
#return type: void
def connectToSession(s):    
    host = "127.0.0.1"
    port = 8080
    #host = input("Enter session IP: ")
    #port = int(input("Enter session Port: "))
    password = getpass("Enter session password: ")
    username = "[" + input("Enter your session name: ") + "] " 
    s.connect((host, port))

    #before starting threads, we grab the message the server sent us.
    #the message sent was the keys that the server has.
    #we will then send the Server our keys.
    #then both client and server will have gab securely.

    #start threads
    Thread(target=receiveMsg, args=(s, username)).start()
    Thread(target=sendMsg, args=(s, username)).start()

#_____________________________________________________________________________________
#int used as a boolean to determine if chat is still open
session_open = 1
#this bottom variable needs to be global for both client and server to read it.
#Threads cannot store values, so it is manditory for this as global inorder change it's value
gab = 0
ga = 0
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