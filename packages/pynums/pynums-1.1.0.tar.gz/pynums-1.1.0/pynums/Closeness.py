import math
try:
    class closeness():
        def ClosenessToPi(number: float) -> float:
            result = 100 * (1 - abs(number - math.pi) / math.pi)

            return result

        def ClosenessToE(number: float) -> float:
            result = 100 * (1 - abs(number - math.e) / math.e)

            return result
    
        def ClosenessBetweenNumbers(a: float, b: float) -> float:
            result = 100 * (1 - abs(a - b) / max(abs(a), abs(b)))

            return result
except TypeError:
    print("TypeError")
