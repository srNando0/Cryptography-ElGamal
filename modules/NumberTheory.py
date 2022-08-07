import secrets



#
#	+---------------
#	| Classes
#	+---------------
#
class NumberTheory:
	"""
	Class of essential functions from number theory
	"""
	
	
	
	#
	#	+---------------
	#	| Integer Functions
	#	+---------------
	#
	def euclidean(number1: int, number2: int) -> int:
		"""
		Does the euclidean algorithm
		
		Args:
			number1 (int): greatest common divisor argument
			number2 (int): greatest common divisor argument
		
		Returns:
			int: greatest common divisor between number1 and number2
		"""
		remainderList = [number1, number2]
		
		while remainderList[1] != 0:
			quotient = remainderList[0]//remainderList[1]
			remainder = remainderList[0] - quotient*remainderList[1]
			
			remainderList[0] = remainderList[1]
			remainderList[1] = remainder
		
		return remainderList[0]
	
	
	
	def extendedEuclidean(number1: int, number2: int) -> tuple[int, int, int]:
		"""
		Does the extended euclidean algorithm
		
		Args:
			number1 (int): first diofantine equation number
			number2 (int): second diofantine equation number
		
		Returns:
			tuple[int, int, int]: two coefficients solving the diofantine equation, and the gdc
		"""
		alphaList = [1, 0]
		betaList = [0, 1]
		remainderList = [number1, number2]
		
		while remainderList[1] != 0:
			quotient = remainderList[0]//remainderList[1]
			
			alpha = alphaList[0] - quotient*alphaList[1]
			beta = betaList[0] - quotient*betaList[1]
			remainder = remainderList[0] - quotient*remainderList[1]
			
			alphaList[0] = alphaList[1]
			alphaList[1] = alpha
			betaList[0] = betaList[1]
			betaList[1] = beta
			remainderList[0] = remainderList[1]
			remainderList[1] = remainder
		
		return (alphaList[0], betaList[0], remainderList[0])
	
	
	
	def sqrt(number: int) -> int:
		"""
		Square root using the babylonian algorithm
		
		Args:
			number (int): number for extracting the square root
		
		Returns:
			int: floor of the square root of number
		"""
		x = number
		y = 1
		
		while(y < x):
			x = (x + y) >> 1
			y = number // x
		
		return x
	
	
	
	def ceilSqrt(number: int) -> int:
		"""
		ceil of the square root
		
		Args:
			number (int): number for extracting the square root
		
		Returns:
			int: ceil of the square root of number
		"""
		return 1 + NumberTheory.sqrt(number - 1)
	
	
	
	#
	#	+---------------
	#	| Prime Functions
	#	+---------------
	#
	def fermatTest(n: int, bList: list[int]) -> bool:
		"""
		Primality test based on Fermat's little theorem
		
		Args:
			n (int): number to be tested
			bList (list[int]): list of bases
		
		Returns:
			bool: False if n is composite, True if n is probably prime
		"""
		#                            n - 1
		# for each base b, check if b      = 1 (mod n)
		for b in bList:
			if NumberTheory.modularExponentiation(b, n - 1, n) == 1:
				continue
			else:
				return False
		
		return True
	
	
	
	def millerRabin(n: int, bList: list[int]) -> bool:
		"""
		Does the Miller-Rabin primality test
		
		Args:
			n (int): number to be tested
			bList (list[int]): list of bases
		
		Returns:
			bool: False if n composite, True if n is probably prime
		"""
		# not primes or even primes
		if n == 2:
			return True
		elif n < 2 or n & 1 == 0:
			return False
		
		#                                           s
		# getting the contants s and d for n - 1 = 2  d
		d = n - 1
		s = 0
		
		while d & 1 == 0:
			s += 1
			d >>= 1
		
		# Miller-Rabin core.
		#
		# idea:
		#  2
		# x  - 1 = (x + 1)(x - 1) (mod n).
		# if n is prime, n must divide only one of them
		for b in bList:
			#  d
			# b
			power = NumberTheory.modularExponentiation(b, d, n)
			
			# in case of n prime
			#     d   +
			# if b  = - 1 (mod n), then n can't divide other factors
			if power == 1 or power == n - 1:
				continue
			# if not, n must divide another factor
			
			#                        i
			#                       2  d
			# testing if n divides b     + 1
			#                                  s
			#                                 2  d
			# which are the other factors of b     - 1
			nDivides = False
			for _ in range(s - 1):
				#         2
				# /   i  \     i + 1
				# |  2  d|    2      d
				# \b     / = b         (mod n)
				power = (power*power)%n
				
				# test
				if power == n - 1:
					nDivides = True
					continue
			#                                                           s
			#                                                          2  d
			# if n is prime, then n must divide one of the factors of b     - 1
			# otherwise, n cant be prime
			if not nDivides:
				return False
		
		# if passes all tests, then n is probably prime
		return True
	
	
	
	def millerRabin64Deterministic(n: int) -> bool:
		"""
		Does a 64-bit number deterministic Miller-Rabin primality test
		
		Args:
			n (int): number to be tested
		
		Returns:
			bool: False if n composite, True if n is prime for a 64-bit n
		"""
		bList = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
		return NumberTheory.millerRabin(n, bList)
	
	
	
	def sieveOfEratosthenes(maxNumber: int) -> list[int]:
		"""
		Does the sieve of Eratosthenes (with two improvements)
		
		Args:
			maxNumber (int): a number for searching primes less than or equal to that number
		
		Returns:
			list[int]: a list of all primes less than or equal to maxNumber
		"""
		# list of booleans that tells us that isPrimeList[p] == True iff p is prime
		isPrimeList: list[bool] = [True]*(maxNumber + 1)
		
		# 0 and 1 are not primes
		isPrimeList[0] = False
		isPrimeList[1] = False
		
		# stating with 2
		p = 2
		
		# while p is not the square root of maxNumber
		while (p*p <= maxNumber):
			# skip if p is not prime
			if not isPrimeList[p]:
				p += 1
				continue
			
			#                2
			# starting from p  because:
			# numbers with factors less than p was already removed
			p2 = p*p
			while (p2 <= maxNumber):
				isPrimeList[p2] = False
				p2 += p
			
			# next prime
			p += 1
		
		# creating the list of primes less than or equal to maxNumber
		primeList: list[int] = []
		for p in range(0, maxNumber + 1):
			if isPrimeList[p]:
				primeList.append(p)
		
		return primeList
	
	
	
	def sieveOfEratosthenesForMillerRabin(number: int) -> list[int]:
		"""
		Does the sieve of Eratosthenes for almost deterministic Miller-Rabin
		
		Args:
			number (int): the number to be tested in fast primality test
		
		Returns:
			list[int]: a list of all primes less than O(log n/log log n)
		"""
		# getting O(log n)
		n = number
		log = 0
		while n != 0:
			n >>= 1
			log += 1
		
		#                                                          /  x  \
		# prime list for trial division and Miller-Rabin. pi(x) ~ O|-----|
		#                                                          \log x/
		return NumberTheory.sieveOfEratosthenes((log >> 1) + 1)
	
	
	
	def fastPrimalityTest(n: int, dList: list[int], bList: list[int]) -> bool:
		"""
		Does a fast primality test using trial division, Fermat's test on base 2, and Miller-Rabin test
		
		Args:
			n (int): number to be tested
			maxNumber (list[int): list of bases for Miller-Rabin
		
		Returns:
			bool: False if the number is composite, True if the number is probably prime
		"""
		# |n| = length of word that represents the number n
		#     could be number of bits of n
		
		# not primes or even primes: O(|n|)
		if n == 2:
			return True
		elif n < 2 or n & 1 == 0:
			return False
		
		#                        2
		# trial division: O(d |n| )
		for d in dList:
			if n%d == 0:
				return n == d
		
		#                               3
		# Fermat's test in base 2: O(|n| )
		if not NumberTheory.fermatTest(n, [2]):
			return False
		
		#                           3
		# Miller-Rabin test: O(b |n| )
		return NumberTheory.millerRabin(n, bList)
	
	
	
	def previousPrime(number: int) -> int:
		"""
		Gets the previous prime
		
		Args:
			number (int): start number from where the search for primes begins
		
		Returns:
			int: the greatest probable prime less than or equal to number
		"""
		# number must be greater than 2
		if number <= 2:
			return 2
		
		# if number is even, begin with number - 1
		prime = number
		if prime & 1 == 0:
			prime -= 1
		
		#   b
		# -----
		# log b
		pList = NumberTheory.sieveOfEratosthenesForMillerRabin(prime)
		
		# while not prime, decrement by 2
		while not NumberTheory.fastPrimalityTest(prime, pList, pList):
			prime -= 2
		
		return prime
	
	
	
	def nextPrime(number: int) -> int:
		"""
		Gets the next prime
		
		Args:
			number (int): start number from where the search for primes begins
		
		Returns:
			int: the smallest probable prime greater than or equal to number
		"""
		# if number is even, begin with number + 1
		prime = number
		if prime & 1 == 0:
			prime += 1
		
		#   b
		# -----
		# log b
		pList = NumberTheory.sieveOfEratosthenesForMillerRabin(prime)
		
		# while not prime, decrement by 2
		while not NumberTheory.fastPrimalityTest(prime, pList, pList):
			prime -= 2
		
		return prime
	
	
	
	def factorizationTrialDivision(number: int) -> list[tuple[int, int]]:
		"""
		Factors a given number using trial division
		
		Args:
			number (int): the number to be factored
		
		Returns:
			list[tuple[int, int]]: the factorization given by a list of pairs composed of a prime and its exponent
		"""
		n = number	# number to be factored
		#   _
		# \/n
		sqrtN = NumberTheory.sqrt(n)
		
		factorization: list[tuple[int, int]] = []	# list of factors
		d = 2										# current divisor
		
		#              _
		# while d <= \/n
		while d <= sqrtN:
			if n%d == 0:
				#      e
				# n = d  n'
				e = 0
				while n%d == 0:
					n //= d
					e += 1
				
				# updates square root and insert the power of d on the list
				sqrtN = NumberTheory.sqrt(n)
				factorization.append((d, e))
			
			# increments d
			d += 1
		
		#      _
		# if \/n < d, then n is prime
		if n != 1:
			factorization.append((n, 1))
		
		return factorization
	
	
	
	#
	#	+---------------
	#	| Modulo Functions
	#	+---------------
	#
	def multiplicativeInverse(number: int, modulo: int) -> int:
		"""
		Does an extended euclidean algorithm for computing the multiplicative inverse
		
		Args:
			number (int): number for finding its inverse
			modulo (int): the modulo of Z set
		
		Returns:
			int: the multiplicative inverse if it exists, otherwise 0
		"""
		alphaList = [1, 0]
		remainderList = [number, modulo]
		
		while(remainderList[1] != 0):
			quotient = remainderList[0]//remainderList[1]
			
			alpha = (alphaList[0] - (quotient*alphaList[1])%modulo)%modulo
			remainder = remainderList[0] - quotient*remainderList[1]
			
			alphaList[0] = alphaList[1]
			alphaList[1] = alpha
			remainderList[0] = remainderList[1]
			remainderList[1] = remainder
		
		return alphaList[0] if remainderList[0] == 1 else 0
	
	
	
	def modularExponentiation(base: int, exponent: int, modulo: int) -> int:
		"""
		Does the fast binary modular exponentiation
		
		Args:
			base (int): base of the exponentiation
			exponent (int): exponent of the exponentiation
			modulo (int): modulo of the exponentiation
		
		Returns:
			int: base^exponent (mod modulo)
		"""
		p = 1
		b = base
		e = exponent
		
		while(0 < e):
			if e & 1 == 1:
				p = (p*b)%modulo
			
			e >>= 1
			b = (b*b)%modulo
		
		return p
	
	
	
	def primitiveRoot(factorization: list[tuple[int, int]], p: int) -> int:
		"""
		Finds a primitive root modulo p using the Gauss's algorithm
		
		Args:
			factorization (list[tuple[int, int]]): factors of p - 1
			p (int): modulo of Z_p
		
		Returns:
			int: primitive root modulo p
		"""
		g = 1
		
		for q, e in factorization:
			#                   p - 1
			#                   -----
			#                     q
			# find a such that a      =/= 1 (mod p)
			n = (p - 1)//q
			a = 2
			
			while NumberTheory.modularExponentiation(a, n, p) == 1:
				a += 1
			
			#    p - 1
			#    -----
			#       e
			#      q
			# h = a
			h = NumberTheory.modularExponentiation(a, (p - 1)//(q**e), p)
			
			# g = h  ... h
			#      1      n
			g = (g*h)%p
		
		return g
				
				
	
	
	
	#
	#	+---------------
	#	| Random Functions
	#	+---------------
	#
	def randomNumberInRange(lowerBound: int, upperBound: int) -> int:
		"""
		Generates a random number in a range (inclusive both sides)
		
		Args:
			lowerBound (int): the smallest number that can be generated
			upperBound (int): the greatest number that can be generated
		
		Returns:
			int: a number such that lowerBound <= number <= upperBound
		"""
		return lowerBound + secrets.randbelow(upperBound + 1)
	
	
	
	def randomBits(bits: int) -> int:
		"""
		Generates a random number by choosing random bits
		
		Args:
			bits (int): number of bits to be randomized
		
		Returns:
			int: the generated number
		"""
		return secrets.randbits(bits)
	
	
	
	def randomBigInteger(bits: int) -> int:
		"""
		Generates a random number with a given number of bits
		
		Args:
			bits (int): number of bits the number must have
		
		Returns:
			int: the generated number
		"""
		return NumberTheory.randomBits(bits - 1) + (1 << (bits - 1))
	
	
	
	#
	#	+---------------
	#	| Recycle Bin
	#	+---------------
	#
	# test if n is in the (2x + 1)(4x + 1) form
	# roots of (2x + 1)(4x + 1) - n:
	#             ______
	#     -3 +- \/8n + 1         ______
	# x = -------------- <===> \/8n + 1 = +-3 (mod 8)
	#           8
	#sqrt = NumberTheory.sqrt(8*n + 1)%8
	#if sqrt == 3 or sqrt == 5:
	#	return False
	
	# test if n is in the (2x + 1)(6x + 1) form
	# roots of (2x + 1)(6x + 1) - n:
	#             ______
	#     -2 +- \/3n + 1         ______
	# x = -------------- <===> \/3n + 1 = +- 2 (mod 6)
	#           6
	#sqrt = NumberTheory.sqrt(3*n + 1)%6
	#if sqrt == 2 or sqrt == 4:
	#	return False



#	+---------------


