class Digits():
    try:
        def SumDigits(x):
            result = 1

            for i in str(abs(x)):
                result += int(i)
            return result

        def MultiplicationDigits(x):
            result = 1

            for i in str(abs(x)):
                result *= int(i)
            return result

        def MinusDigits(x):
            result = 1

            for i in str(abs(x)):
                result -= int(i)
            return result

        def DivisionDigits(x):
            result = 1

            for i in str(abs(x)):
                result /= int(i)
            return result
    
        def DigitsCount(x):
            return len(str(abs(x)))
    
        def DigitFrequency(x):
            freq = {}
            for i in str(abs(x)):
                freq[i] = freq.get(i, 0) + 1
            return freq
    except TypeError:
        print("TypeError")
            