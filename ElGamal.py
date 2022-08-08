from tokenize import Number
from modules.NumberTheory import NumberTheory

import base64
import json

# print-test
import time



#
#	+---------------
#	| Classes
#	+---------------
#
class ElGamal:
	"""
	Implementation of the ElGamal cryptography
	"""
	
	
	
	#
	#	+---------------
	#	| Generation Methods
	#	+---------------
	#
	def generateSafeCyclicGroup(self, bits: int) -> None:
		"""
		Generates the multiplicative group Z_p with p begin a safe prime, take its generator and its order
		
		Args:
			bits (int): approximately the number of bits of the prime modulo
		"""
		bigNumber = NumberTheory.randomBigInteger(bits)
		
		# p, q are primes
		# q divides p - 1, therefore there is an integer c such that
		#     cq = p - 1
		# because p - 1 is even and q is odd, then c must be even
		# therefore, there is an integer k such that
		#     2kq = p - 1
		# therefore
		#     p = 2kq + 1
		q = NumberTheory.nextPrime(bigNumber)
		_2q = q << 1
		p = _2q + 1
		k = 1
		
		pList = NumberTheory.sieveOfEratosthenesForAlmostDeterministicMillerRabin(p)
		
		while not NumberTheory.fastPrimalityTest(p, pList, pList):
			# p(k + 1) = 2(k + 1)q + 1 = (2kq + 1) + 2q = p(k) + 2q
			p += _2q
			k += 1
		
		# getting information about the cyclic group
		self.modulo = p
		self.order = p - 1
		
		self.orderFactorization = NumberTheory.factorizationTrialDivision(2*k)
		self.orderFactorization.append((q, 1))
		
		self.generator = NumberTheory.primitiveRoot(self.orderFactorization, p)
		
		# calculating the number of bits and bytes of modulo
		self.bits = bits
		p >>= bits
		
		while 0 < p:
			p >>= 1
			self.bits += 1
		
		self.bytes = (self.bits>>3) + (0 if self.bits>>3 == 0 else 1)
	
	
	
	def generateCyclicGroup(self, bits: int) -> None:
		"""
		Generates the multiplicative group Z_p with p prime, take a generator and its order
		
		Args:
			bits (int): approximately the number of bits of the prime modulo
		"""
		# generating prime
		bigNumber = NumberTheory.randomBigInteger(bits)
		p = NumberTheory.nextPrime(bigNumber)
		
		# getting information about the cyclic group
		self.modulo = p
		self.order = p - 1
		self.orderFactorization: list[tuple[int, int]] = []
		self.generator = NumberTheory.randomNumberInRange(0, self.modulo - 1)
		
		# calculating the number of bits and bytes of modulo
		self.bits = bits
		p >>= bits
		
		while 0 < p:
			p >>= 1
			self.bits += 1
		
		self.bytes = self.bits>>3 + (0 if self.bits>>3 == 0 else 1)
	
	
	
	def generateSimpleGroup(self, bits: int) -> None:
		"""
		Generates the multiplicative group Z_n, take a probable random generator and an upper bound of its order
		
		Args:
			bits (int): number of bits of the modulo
		"""
		self.modulo = NumberTheory.randomBigInteger(bits)
		self.order = self.modulo - 1
		
		self.generator = NumberTheory.randomNumberInRange(2, self.modulo - 2)
		
		while NumberTheory.euclidean(self.generator, self.modulo) != 1:
			self.generator += 1
		
		# calculating the number of bits and bytes of modulo
		self.bits = bits
		self.bytes = self.bits>>3 + (0 if self.bits>>3 == 0 else 1)
	
	
	
	def generateKeys(self) -> None:
		"""
		Generates a public and private keys
		"""
		# non obvious private key
		minKey = self.order//8
		self.privateKey = NumberTheory.randomNumberInRange(minKey, self.order - 1 - minKey)
		
		# public key
		self.publicKey = NumberTheory.modularExponentiation(self.generator, self.privateKey, self.modulo)
		
		# inverse of public key
		self.publicKeyInverse = NumberTheory.multiplicativeInverse(self.publicKey, self.modulo)
	
	
	
	#
	#	+---------------
	#	| Encryption and Decryption Methods
	#	+---------------
	#
	def encryptJSON(self, jsonData: str, publicKey: int, usePrivateKey: bool = False) -> str:
		"""
		Encrypts JSON data
		
		Args:
			jsonData (str): jsonData to be encrypted
			publicKey (int): public key used to encrypt
			usePrivateKey (bool, optional): if True, uses the private key to encrypt. Defaults to False.
		
		Returns:
			tuple[list[int], int]: cipher in JSON format
		"""
		# generating the key exponent
		if usePrivateKey:
			keyExponent = self.privateKey
		else:
			minKey = self.order//8
			keyExponent = NumberTheory.randomNumberInRange(minKey, self.order - 1 - minKey)
		
		# calculating the key
		key = NumberTheory.modularExponentiation(self.generator, keyExponent, self.modulo)
		sharedKey = NumberTheory.modularExponentiation(publicKey, keyExponent, self.modulo)
		
		# encrypting data
		data = jsonData.encode("utf-8")
		blockList = ElGamal.dataSlices(data, self.bytes - 1)
		
		cipher = b''
		for block in blockList:
			blockNumber = int.from_bytes(block, "little")
			cipherNumber = (blockNumber*sharedKey)%self.modulo
			cipher += cipherNumber.to_bytes(self.bytes, "little")
		
		# returning the cipher in json format
		jsonCipher = {
			"length": len(data),
			"cipher": base64.b64encode(cipher).decode("utf-8"),
			"key": base64.b64encode(key.to_bytes(self.bytes, "little")).decode("utf-8")
		}
		
		return json.dumps(jsonCipher, separators = (',', ':'))
	
	
	
	def decryptJSON(self, jsonCypher: str) -> str:
		"""
		Decrypts JSON cipher
		
		Args:
			jsonCypher (str): the cipher to be decrypted in json format
		
		Returns:
			bytes: the decrypted data in json format
		"""
		# getting the cipher data from JSON
		dictionary = json.loads(jsonCypher)
		length = dictionary["length"]
		
		# getting keys
		keyBytes = base64.b64decode(dictionary["key"])
		key = int.from_bytes(keyBytes, "little")
		sharedKey = NumberTheory.modularExponentiation(key, self.privateKey, self.modulo)
		sharedKeyInverse = NumberTheory.multiplicativeInverse(sharedKey, self.modulo)
		
		# decrypting cipher 
		cipher = base64.b64decode(dictionary["cipher"])
		blockList = ElGamal.dataSlices(cipher, self.bytes)
		
		data = b''
		for block in blockList:
			blockNumber = int.from_bytes(block, "little")
			dataNumber = (blockNumber*sharedKeyInverse)%self.modulo
			data += dataNumber.to_bytes(self.bytes - 1, "little")
		
		return data[:length].decode("utf-8")
	
	
	
	def encryptNumber(self, number: int, publicKey: int) -> tuple[int, int]:
		"""
		Encrypts a number
		
		Args:
			number (int): a number to be encripted
			publicKey (int): public key used to encript
		
		Returns:
			tuple[int, int]: the cipher consisting of an encrypted number and a power of generator
		"""
		randomNumber = NumberTheory.randomNumberInRange(0, self.modulo - 1)
		randomPower = NumberTheory.modularExponentiation(self.generator, randomNumber, self.modulo)
		sharedKey = NumberTheory.modularExponentiation(publicKey, randomNumber, self.modulo)
		return ((number*sharedKey)%self.modulo, randomPower)
	
	
	
	def decryptNumber(self, cipher: tuple[int, int]) -> tuple[int, int]:
		"""
		Decrypts a number
		
		Args:
			cipher (tuple[int, int]): a cipher consisting of an encrypted number and a power of generator
		
		Returns:
			tuple[int, int]: the decrypted cipher number
		"""
		encryptedNumber, power = cipher
		sharedKey = NumberTheory.modularExponentiation(power, self.privateKey, self.modulo)
		sharedKeyInverse = NumberTheory.multiplicativeInverse(sharedKey, self.modulo)
		return (encryptedNumber*sharedKeyInverse)%self.modulo
	
	
	
	#
	#	+---------------
	#	| Auxiliary Functions
	#	+---------------
	#
	def dataSlices(data: bytes, numBytes: int) -> list[bytes]:
		"""
		Slices the data into integer blocks with a given number of bytes of length
		
		Args:
			data (bytes): the data to be sliced
			numBytes (int): number of bytes of block length
		
		Returns:
			list[int]: a list of blocks
		"""
		blockList: list[int] = []
		
		#                    +- len(data) -+
		# number of slices = |  ---------  |
		#                    |  numBytes   |
		blockListSize = len(data)//numBytes + (0 if len(data)%numBytes == 0 else 1)
		
		for i in range(blockListSize):
			slice = data[i*numBytes:(i + 1)*numBytes]
			blockList.append(slice)
		
		return blockList
	
	
	
	#
	#	+---------------
	#	| Getters and Setters
	#	+---------------
	#
	def getGroup(self) -> tuple[int, int, list[tuple[int, int]], int, int, int]:
		"""Gets the group data"""
		return (self.modulo, self.order, self.orderFactorization, self.generator, self.bits, self.bytes)
	
	def getPublicKey(self) -> int:
		"""Gets the public key"""
		return self.publicKey
	
	
	
	def setGroup(self, group: tuple[int, int, int, int]) -> None:
		"""Sets the group data"""
		self.modulo, self.order, self.orderFactorization, self.generator, self.bits, self.bytes = group



#	+---------------



#
#	+---------------
#	| Main
#	+---------------
#
bits = 2**10

Alice = ElGamal()
Bob = ElGamal()

# time test
tests = 10

totalTime = 0.0
totalBits = 0.0
percentage = 0.1

for i in range(tests):
	deltaNanoTime = time.time_ns()
	Alice.generateSafeCyclicGroup(bits)
	deltaNanoTime = time.time_ns() - deltaNanoTime
	
	currentTime = deltaNanoTime/1_000_000
	
	while percentage*tests - 0.001 < i:
		print(f'{"{:.0f}".format(percentage*100)}%')
		percentage += 0.1
	
	totalTime += currentTime
	totalBits += Alice.bits
	

averageTime = totalTime/tests
averageBits = totalBits/tests

print(f'\nAverage time: {"{:.2f}".format(averageTime)}ms\nAverage bit length: {averageBits}\n\n\n')

print(f'Time required to generate group: {"{:.2f}".format(deltaNanoTime/1_000_000)}ms\n\
|   {Alice.bits}-bit prime\n|   Modulo:\n{Alice.modulo}\n|   Generator:\n{Alice.generator}\n|   Order:\n{Alice.order}\n\n\n')




Bob.setGroup(Alice.getGroup())

Bob.generateKeys()

message = input("Write a message: ")
print(f'\
================\n\
sent message:\n\
{message}\n\
================\n')
cipher = Alice.encryptJSON(message, Bob.publicKey)
print(f'\
================\n\
cipher:\n\
{cipher}\n\
================\n')
recvMsg = Bob.decryptJSON(cipher)
print(f'\
================\n\
received message:\n\
{recvMsg}\n\
================\n')

'''
deltaNanoTime = time.time_ns()
Alice.generateSafeCyclicGroup(bits)
deltaNanoTime = time.time_ns() - deltaNanoTime

print(f'Time required to generate group: {"{:.2f}".format(deltaNanoTime/1_000_000)}ms\n\
|   {Alice.bits}-bit prime\n|   Modulo:\n{Alice.modulo}\n|   Generator:\n{Alice.generator}\n|   Order:\n{Alice.order}')



print('\n\n----------------\n')



deltaNanoTime = time.time_ns()
Alice.generateCyclicGroup(bits)
deltaNanoTime = time.time_ns() - deltaNanoTime

print(f'Time required to generate group: {"{:.2f}".format(deltaNanoTime/1_000_000)}ms\n\
|   {Alice.bits}-bit prime\n|   Modulo:\n{Alice.modulo}\n|   Generator:\n{Alice.generator}\n|   Order:\n{Alice.order}')



print('\n\n----------------\n')



deltaNanoTime = time.time_ns()
Alice.generateSimpleGroup(bits)
deltaNanoTime = time.time_ns() - deltaNanoTime

print(f'Time required to generate group: {"{:.2f}".format(deltaNanoTime/1_000_000)}ms\n\
|   Modulo:\n{Alice.modulo}\n|   Generator:\n{Alice.generator}\n|   Order:\n{Alice.order}')
'''


'''
Bob.setGroup(Alice.getGroup())

Bob.generateKeys()

randomNumber = 0
decryptedNumber = 0

while randomNumber == decryptedNumber:
	randomNumber = NumberTheory.randomBigInteger(bits)%Alice.modulo
	#print(randomNumber)
	cipher = Alice.encryptNumber(randomNumber, Bob.getPublicKey())
	#print(cipher)
	decryptedNumber = Bob.decryptNumber(cipher)
	print(randomNumber == decryptedNumber)

print(f'Alice: {randomNumber}\nBob: {decryptedNumber}')'''



#	+---------------



#
#	+---------------
#	| Comment Layouts
#	+---------------
#

#
#	+---------------
#	| Section
#	+---------------
#

#	+---------------
