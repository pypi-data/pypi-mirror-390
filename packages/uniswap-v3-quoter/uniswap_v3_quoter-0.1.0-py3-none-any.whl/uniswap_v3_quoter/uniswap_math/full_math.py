"""
FullMath Library
Ported from Solidity: v3-core/contracts/libraries/FullMath.sol

Facilitates multiplication and division that can have overflow of an intermediate value without any loss of precision
Handles "phantom overflow" i.e., allows multiplication and division where an intermediate value overflows 256 bits
"""


def mul_div(a: int, b: int, denominator: int) -> int:
    """
    Calculates floor(a×b÷denominator) with full precision.
    Throws if result overflows a uint256 or denominator == 0
    
    Credit to Remco Bloemen under MIT license https://xn--2-umb.com/21/muldiv
    
    Args:
        a: The multiplicand
        b: The multiplier
        denominator: The divisor
        
    Returns:
        The 256-bit result
    """
    assert denominator > 0, "Denominator must be greater than 0"
    
    # 512-bit multiply [prod1 prod0] = a * b
    # Compute the product mod 2**256 and mod 2**256 - 1
    prod0 = (a * b) & ((1 << 256) - 1)  # Least significant 256 bits
    prod1 = (a * b) >> 256  # Most significant 256 bits
    
    # Handle non-overflow cases, 256 by 256 division
    if prod1 == 0:
        return prod0 // denominator
    
    # Make sure the result is less than 2**256
    assert denominator > prod1, "Result overflows uint256"
    
    ###############################################
    # 512 by 256 division.
    ###############################################
    
    # Make division exact by subtracting the remainder from [prod1 prod0]
    remainder = (a * b) % denominator
    
    # Subtract 256 bit number from 512 bit number
    prod1 -= 1 if remainder > prod0 else 0
    prod0 = (prod0 - remainder) & ((1 << 256) - 1)
    
    # Factor powers of two out of denominator
    # Compute largest power of two divisor of denominator (always >= 1)
    twos = denominator & (~denominator + 1)
    
    # Divide denominator by power of two
    denominator //= twos
    
    # Divide [prod1 prod0] by the factors of two
    prod0 //= twos
    
    # Shift in bits from prod1 into prod0
    # Flip twos such that it is 2**256 / twos
    # If twos is zero, then it becomes one
    twos = (((1 << 256) - twos) // twos) + 1
    prod0 |= prod1 * twos
    
    # Invert denominator mod 2**256
    # Now that denominator is an odd number, it has an inverse modulo 2**256
    # such that denominator * inv = 1 mod 2**256.
    # Compute the inverse by starting with a seed that is correct for four bits
    inv = (3 * denominator) ^ 2
    
    # Use Newton-Raphson iteration to improve the precision
    # Thanks to Hensel's lifting lemma, this also works in modular arithmetic
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**8
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**16
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**32
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**64
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**128
    inv = (inv * (2 - denominator * inv)) & ((1 << 256) - 1)  # inverse mod 2**256
    
    # Because the division is now exact we can divide by multiplying with the modular inverse
    result = (prod0 * inv) & ((1 << 256) - 1)
    return result


def mul_div_rounding_up(a: int, b: int, denominator: int) -> int:
    """
    Calculates ceil(a×b÷denominator) with full precision.
    Throws if result overflows a uint256 or denominator == 0
    
    Args:
        a: The multiplicand
        b: The multiplier
        denominator: The divisor
        
    Returns:
        The 256-bit result rounded up
    """
    result = mul_div(a, b, denominator)
    if (a * b) % denominator > 0:
        assert result < (1 << 256) - 1, "Result overflows uint256"
        result += 1
    return result

