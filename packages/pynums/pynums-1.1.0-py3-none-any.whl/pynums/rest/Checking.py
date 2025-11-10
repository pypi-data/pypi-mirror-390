import math

def IsArmstrong(x):
    try:
        digits = str(x)
        power = len(digits)

        result = x == sum(int(i) ** power for i in digits)
        return result
    except TypeError:
        print("TypeError")

def IsPalindromeNumber(x):
    try:
        s = str(abs(x))
        return s == s[::-1]
    except TypeError:
        print("TypeError")

def IsPerfectNumbers(x):
    # Perfect number
    divisiors = [i for i in range(1, x) if x % i == 0]

    return sum(divisiors) == x

def IsFibonacciNumber(x):
    # Checks if a number is a Fibonacci
    return int(math.sqrt(5 * x * x + 4))**2 == 5 * x * x + 4 or \
                                                int(math.sqrt(5 * x * x - 4))**2 == 5 * x * x - 4

