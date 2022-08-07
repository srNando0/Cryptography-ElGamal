# Cryptography-ElGamal
## Implementation of ElGamal system

In this repository, I implement the ElGamal cryptosystem in Python using the multiplicative group $\mathbb{Z}_n$.  
This implementation can:
- Generate a cyclic group based on safe primes, which are primes $p$ where there is another prime $q$ and an integer $k$ such that $p = kq + 1$.  
Can also find a generator and its order very fast.
- Generate a cyclic group $\mathbb{Z}_p$ with $p$ prime, but guesses a generator and its order.
- Generate a random group $\mathbb{Z}_n$, take a random element as generator and uses a upper bound order.
- Encrypt and Decrypt strings (JSON) and numbers

There is also an implementation of a series of number theory algorithms such:
- Euclidean algorithm and extended euclidean algorithm.
- Square root using the babylonian algorithm, and also an implementation of its ceil.
- Fermat primality test.
- Miller-Rabin primality test.
- Sieve of Eratosthenes and its version for almost deterministic Miller-Rabin.
- A fast primality test using 3 stages:  
$O(\frac{\log n}{\log \log n})$ trial divisions, Fermat in base 2, and finally Miller-Rabin.
- An algorithm to get the previous or next prime after a given number.
- Trial division factorization algorithm $O(\sqrt n)$ time complexity.
- Algorithm for finding multiplicative inverse based on extended euclidean algorithm $O(n)$ space complexity.
- Modular exponentiation by squaring.
- Gauss's algorithm for finding primitive roots.
