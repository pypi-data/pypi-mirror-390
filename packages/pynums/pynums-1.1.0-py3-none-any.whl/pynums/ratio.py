try:
    class ratio():
        def RatioEvenOdd(x):
            evens = len([i for i in x if i % 2 == 0])

            odds = len(x) - evens
            result = evens / odds if odds != 0 else float('inf')

            return result
    
        def ClosenessToGoldenRatio(number: float) -> float:
            golden = (1 + 5 ** 0.5) / 2

            result = 100 * (1 - abs(number - golden) / golden)
            return result
except TypeError:
    print("TypeError")
