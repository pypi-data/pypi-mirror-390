import math

try:
    def ReverseNumber(x):
        sign = -1 if x < 0 else 1
        result = sign * int(str(abs(x)) [::-1]) 

        return result
    
    def ToBinarySum(x):
        binaries = [bin(i)[2:] for i in x]

        print(binaries)

        return sum(x)

    def RoundToHearest(x, base=5):
        result = round(x / base) * base

        return result

    def gcdList(x):
        result = x[0]
        for i in x[1:]:
            result = math.gcd(result, i)
        return result

    def lcmList(x):
        result = x[0]
        for i in x[1:]:
            result = abs(result * i) // math.gcd(result, i)
        return result

    def precent(x, y):
        return (
            (x / y) * 100 if y != 0 else 0, "%"
        )
except TypeError:
    print("TypeError")
    