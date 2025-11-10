import math

try:
    # Calcutions
    def derivative(f, x, h=1e-7):
        # Numerical approximation of the derivative of a function at a point
        return (f(x + h) - f(x - h)) / (2 * h)

    def integral(f, a, b, n=10000):
        # Numerical integation by the traoezoid mehod 
        step = (b - a) / n
        total = 0.5 * (f(a) + f(b))

        for i in range(1, n):
            total += f(a + i * step)

        return total * step

    def NewtonRaphson(f, df, x0, tol=1e-6, max_iter=100):
        # Newton's method for finding roots
        x = x0

        for _ in range(max_iter):
            fx = f(x)
            dfx = df(x)
            if abs(fx) < tol:
                return x
            if dfx == 0:
                raise ValueError()
            x -= fx / dfx
        return x

    # work with equations
    def QadraticSolver(a, b, c):
        # solves qadratic equations

        d = b ** 2 - 4 * a * c
        if d < 0:
            return None
        elif d == 0:
            return (-b / (2 * a), )
        else:
            sqrt_d = math.sqrt(d)
            return ((-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a))

    def SystemLinear2x2(a1, b1, c1, a2, b2, c2):
        # Solves a system of two linear equations

        det = a1 * b2 - a2 * b1
        if det == 0:
            return None
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        return x, y

    # Number Theoretic Function
    def IsMersennePrime(p):
        # Checks whether 2^p - 1 is prime
        n = 2 ** p - 1
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
            return True

    def CollatzSteps(x):
        # Number of steps of the Colltaz cojecture
        count = 0
        while x != 1:
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            count += 1
        return count

    # Matrix and vector math
    def DotProduct(a, b):
        # Scalar product
        return sum(i * j for i, j in zip(a, b))

    def MatrixMultiply(A, B):
        # Matrix multiplication
        rows_A, cols_A = len(A), len(A[0])
        rows_B, cols_B = len(B), len(B[0])

        if cols_A != rows_B:
            raise ValueError()
    
        result = [[sum(A[i][k] * B[k][j] for k in range(cols_A)) for j in range(cols_B)] for i in range(rows_A)]
        return result
except TypeError:
    print("TypeError")
    