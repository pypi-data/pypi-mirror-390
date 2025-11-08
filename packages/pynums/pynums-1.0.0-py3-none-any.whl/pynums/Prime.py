class Prime():
    def IsPrime(x):
        try:
            if x < 2:
                return False
            for i in range(2, int(x ** 0.5) + 1):
                if x % i == 0:
                    return False
            return True
        except TypeError:
            print("This List or Tuple")
    
    def NextPrime(x):
        def IsPrime(y):
            if x < 2:
                return False
            for i in range(2, int(x ** 0.5) + 1):
                if x % i == 0:
                    return False
            return True

        try:
            x += 1
            while not IsPrime(x):
                x += 1
            return x
        except TypeError:
            print("This List or Tuple")
            print()
