# pynums

pynums is a simple library for working with numbers, created by Andriy Zhuk.  
It includes functions for:  
- working with numbers ('SumDigits, 'ReverseNumber');
- checking ('IsArmstrong', 'IsPerfectNumbers');  
- basic math ('SumAll', 'SumOfDivision');
- statistics ('difference', 'MeenAbsoluteDifference');  
- hard_math ('QadraticSolver', 'CollatzSteps');
- ratio ('RatioEvenOdd', 'ClosenessToGoldenRatio').

## Exampe of use
python

from pynums import Digits, ratio

a = 583  
b = 834  

print(Digits.SumDigits(a))  
print(ratio.ClosenessToGoldenRatio(b))  

## conclusion
17  
-51344.03466174123  

## Installation
```bash
pip install pynums
