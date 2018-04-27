'''
Author:	Eric Zair
File:	Elgamal.py
Description:	This file contains the Decryption
				for Elgamal public key encryption.

				Note:
					This file will be used as an API
					for an encrypted chat program.
'''
import random


'''
Returns the modular inverse of a number.
Parameters: 
			int a(the number you want the inverse of)
			int b(your prime p value)
Return type: int
'''
def extendedEgcd(a, b):
	original_b = b
	x1, x2 = 1, 0
	y1, y2 = 0, 1
	while b:
		q = a//b
		x2, x1 = (x1 - q*x2), x2
		y2, y1 = (y1 - q*y2), y2
		a, b = b, (a - q*b)
	if x1 < 0:
		x1 += original_b
	return x1


#checks to see if a number is prime
#parameters: 
#			int num(the number you want to check if prime)
#Return type: boolean
def isprime(num):
	for i in range(200):
		rand = random.randint(2, num-1)
	return pow(rand, num-1, num) != 1


#Generate big random prime numbers
#Return integers: p
def generateRandomPrime(bit_length):
	p = random.getrandbits(bit_length) | 2^(bit_length) | 1
	while not isprime(p):
		p = random.getrandbits(bit_length) | 2^(bit_length) | 1
	return p

#Generates the random private keys a and b
#return type: int
def generatePrivateKey(bit_length):
	return random.getrandbits(bit_length)


#Returns a Generator g
#return type: int
def generateGenerator(p):
	q = (p-1)/2
	g = random.randint(2, q-1)
	condition1 = pow(g, 1, p) ==  1 % p
	condition2 = pow(g, 2, p) == 1 % p
	condition3 = pow(g, q, p) == 1 % p
	while condition1 or condition2 or condition3:
		g = random.randint(2, q-1)
	return g


#Encrypt any give file.
#parameters: 
#			string filename(name of the file you want to decrypt)
#return type: void
def encrypt(filename):
	#keys and such
	p = generateRandomPrime(300)
	b = generatePrivateKey(300)
	g = generateGenerator(p)
	bob_public_key = pow(g, b, p)

	#file the keys are being logged to 
	key_file = open(filename + ".keys", 'w')
	key_file.write("p = " + str(p))
	key_file.write("\n\na = Value will always change")
	key_file.write("\n\ng^a = Value will always change")
	key_file.write("\n\ng^(ab) = Value will always change")
	key_file.write("\n\nb = " + str(b))
	key_file.write("\n\ng = " + str(g))
	key_file.write("\n\ng^b = " + str(bob_public_key))
	key_file.close()
	
	#Write to the encrypted file.
	encrypted_file = open(filename + ".encrypt", 'w')
	with open(filename, 'r') as file:
		for plain_text in file:
			for m in plain_text:
				a = generatePrivateKey(300)
				private_key = pow(g, a*b, p)
				ga = pow(g, a, p)
				gb = pow(g, a, p)
				encrypted_file.write(str(ord(m) * private_key) + " , " + str(ga) + "\n")
	encrypted_file.close()


#Decrypt the content of any file (file must have also been encrypted with this program)
#parameters:
#			int p (random prime that all keys are modded off of)
#			int b (bob's secret encryption)			
#			string filename (name of the file you are decrypting)
#return type: void
def decrypt(filename, b, p):
	decrypted_filename = filename[0 : filename.index('.txt')] + ".txt.decrypt"
	decrypt_file = open(decrypted_filename, 'w')
	with open(filename, 'r') as file:
		for c in file:
			ga = int(c.split(" , ")[1])
			private_key = pow(ga, b, p)
			m = int(c.split(" , ")[0]) * extendedEgcd(private_key, p) % p
			decrypt_file.write(chr(m))