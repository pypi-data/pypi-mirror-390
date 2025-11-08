"""
LiquidityMath Library
Ported from Solidity: v3-core/contracts/libraries/LiquidityMath.sol

Math library for liquidity
"""


def add_delta(x: int, y: int) -> int:
    """
    Add a signed liquidity delta to liquidity and revert if it overflows or underflows
    
    Args:
        x: The liquidity before change (uint128)
        y: The delta by which liquidity should be changed (int128)
        
    Returns:
        z: The liquidity after change (uint128)
    """
    if y < 0:
        # Convert y to positive for subtraction
        y_abs = -y if y != -(1 << 127) else (1 << 127)  # Handle int128 min
        z = x - y_abs
        assert z < x, "Liquidity underflow"
    else:
        z = x + y
        assert z >= x, "Liquidity overflow"
    
    return z

