from decimal import Decimal, getcontext

# High-precision computing
def HightPrecisioPi(digits=50):
    # calculates the the number Pi with hight accuracy
    getcontext().prec = digits
    pi = Decimal(0)
    k = 0

    while k < digits:
        pi += (Decimal(1)/(16**k))*(
            Decimal(4)/(8*k+1) -
            Decimal(2)/(8*k+4) - 
            Decimal(1)/(8*k+5) - 
            Decimal(1)/(8*k+6)
        )
        k += 1
    return +pi

def FactorialBig(n):
    # factorial of large numbers
    getcontext().prec = len(str(n)) * 2
    result = Decimal(1)

    for i in range(1, n+1):
        result *= i
    return result

# Methods of machine math
def GradientDescent(f, df, start, lr=0.01, epochs=1000):
    # the simplest implementation of gradient descent
    x = start
    for _ in range(epochs):
        x -= lr * df(x)
    return x

def MonteCarloPi(samples=100000):
    # Monte Carlo calculation of pi
    import random
    inside = 0

    for _ in range(samples):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:
            inside += 1
    return 4 * inside / samples

# Machine intelligence functions
def DetectPattern(numbers):
    #  Trying to guess the seqence pattern (difference or multiplier) 
    if len(numbers) < 3:
        return "Not enough data"
    diffs = [numbers[i+1] - numbers[i] 
             for i in range(len(numbers)-1)]
    if len(set(diffs)) == 1:
        return f"Arithmetic progression with difference {diffs[0]}"
    ratios = [numbers[i+1] / numbers[i] for i in range(1, len(numbers)) if numbers[i] != 0]
    if len(set(ratios)) == 1:
        return f"Geometic progression with am multiplier {ratios[0]}"
    return "Unknown pattern"

def EstimatePiRamanujan(interations=5):
    # Calculating pi using Ramunujan formula
    from math import factorial, sqrt

    total = 0
    for k in range(interations):
        total += (factorial(4*k)*(1103 + 26390*k)) / ((factorial(k)**4)*(396**(4*k)))
    return 9801 / (2 * sqrt(2) * total)

def SimulateNeuron(inputs, weights, bias=0):
    # The simplest neuron
    total = sum(i * w for i, w in zip(inputs, weights)) + bias
    return 1 if total > 0 else 0

def PredictLianer(x_values, y_values, new_x):
    # Simple lieanar regresion
    n = len(x_values)
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    num = sum((x - mean_x)*(y - mean_y) for x, y in zip(x_values, y_values))
    den = sum((x - mean_x)**2 for x in x_values)
    slope = num / den
    intercept = mean_y - slope * mean_x

    return slope * new_x + intercept
