class Difference():
    try:
        def difference(x):
            total = max(x) - min(x)
            return total

        def differenceFromDivision(x):
            total = max(x) / min(x)
            return total
    
        def MeenAbsoluteDifference(x):
            diffs = [abs(x[i] - x[i+1]) for i in range(len(x)-1)]

            return sum(diffs) / len(diffs)
    except TypeError:
        print("TypeError")
