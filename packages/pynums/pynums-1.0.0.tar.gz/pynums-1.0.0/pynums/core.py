class Sum():
    def SumAll(x = []):
        total = sum(x)
        return total

    def SumReverse(x = []):
        TotalReverse = x[0]

        for i in x[1:]:
            TotalReverse -= i
        return TotalReverse

    def SumOfDivision(x = []):
        TotalDivision = None

        try:
            TotalDivision = x[0]
            
            for j in x[1:]:
                TotalDivision /= j
            return TotalDivision
        except ZeroDivisionError: 
            print("There is zero on the list", 0)
            
    def SumOfMultiplication(x = []):
        TotalMultiplication = x[0]

        for i in x[1:]:
            TotalMultiplication *= i
        return TotalMultiplication
    
    def ProgressionSum(a1, x, y):
        result = y * (2 * a1 + (y - 1) * x) / 2

        return result
    
    def MirrorSum(a, b):
        def reverse_num(x):
            return int(str(x)[::-1])
        return a + reverse_num(b)
    
    def RangeSum(a, b):
        result = sum(range(a, b + 1))

        return result
