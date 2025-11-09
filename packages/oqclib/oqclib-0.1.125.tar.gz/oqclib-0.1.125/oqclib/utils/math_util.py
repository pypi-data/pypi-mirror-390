
def least_common_multiple(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    import math
    return abs(a * b) // math.gcd(a, b)