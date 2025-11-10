class Sum():
    def SumAll(x = []):
        try:
            total = sum(x)
            return total
        except TypeError:
            print("TypeError")

    def SumReverse(x = []):
        try:
            TotalReverse = x[0]

            for i in x[1:]:
                TotalReverse -= i
            return TotalReverse
        except TypeError:
            print("TypeError")

    def SumOfDivision(x = []):
        try:
            TotalDivision = None

            try:
                TotalDivision = x[0]
            
                for j in x[1:]:
                    TotalDivision /= j
                return TotalDivision
            except ZeroDivisionError: 
                print("There is zero on the list", 0)
        except TypeError:
            print(print("TypeError"))
            
    def SumOfMultiplication(x = []):
        try:
            TotalMultiplication = x[0]

            for i in x[1:]:
                TotalMultiplication *= i
            return TotalMultiplication
        except TypeError:
            print("TypeError")
    
    def ProgressionSum(a1, x, y):
        try:
            result = y * (2 * a1 + (y - 1) * x) / 2

            return result
        except TypeError:
            print("TypeError")
    
    def MirrorSum(a, b):
        try:
            def reverse_num(x):
                return int(str(x)[::-1])
            return a + reverse_num(b)
        except TypeError:
            print("TypeError")
    
    def RangeSum(a, b):
        try:
            result = sum(range(a, b + 1))

            return result
        except TypeError:
            print("TypeError")
