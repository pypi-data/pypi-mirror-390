"""
SqrtPriceMath Library
Ported from Solidity: v3-core/contracts/libraries/SqrtPriceMath.sol

Functions based on Q64.96 sqrt price and liquidity
Contains the math that uses square root of price as a Q64.96 and liquidity to compute deltas
"""

from .full_math import mul_div, mul_div_rounding_up

Q96 = 1 << 96  # 2^96


def _div_rounding_up(x: int, y: int) -> int:
    """Helper: Division rounding up"""
    return (x + y - 1) // y


def get_next_sqrt_price_from_amount0_rounding_up(
    sqrt_px96: int, liquidity: int, amount: int, add: bool
) -> int:
    """
    Gets the next sqrt price given a delta of token0
    Always rounds up
    
    Args:
        sqrt_px96: The starting price (Q64.96)
        liquidity: The amount of usable liquidity
        amount: How much of token0 to add or remove from virtual reserves
        add: Whether to add or remove the amount of token0
        
    Returns:
        The price after adding or removing amount
    """
    if amount == 0:
        return sqrt_px96
    
    numerator1 = liquidity << 96
    
    if add:
        product = amount * sqrt_px96
        if product // amount == sqrt_px96:
            denominator = numerator1 + product
            if denominator >= numerator1:
                return mul_div_rounding_up(numerator1, sqrt_px96, denominator)
        
        return _div_rounding_up(numerator1, (numerator1 // sqrt_px96) + amount)
    else:
        product = amount * sqrt_px96
        assert product // amount == sqrt_px96, "Multiplication overflow"
        assert numerator1 > product, "Denominator underflow"
        denominator = numerator1 - product
        return mul_div_rounding_up(numerator1, sqrt_px96, denominator)


def get_next_sqrt_price_from_amount1_rounding_down(
    sqrt_px96: int, liquidity: int, amount: int, add: bool
) -> int:
    """
    Gets the next sqrt price given a delta of token1
    Always rounds down
    
    Args:
        sqrt_px96: The starting price (Q64.96)
        liquidity: The amount of usable liquidity
        amount: How much of token1 to add or remove from virtual reserves
        add: Whether to add or remove the amount of token1
        
    Returns:
        The price after adding or removing amount
    """
    if add:
        if amount <= ((1 << 160) - 1):
            quotient = (amount << 96) // liquidity
        else:
            quotient = mul_div(amount, Q96, liquidity)
        
        return sqrt_px96 + quotient
    else:
        if amount <= ((1 << 160) - 1):
            quotient = _div_rounding_up(amount << 96, liquidity)
        else:
            quotient = mul_div_rounding_up(amount, Q96, liquidity)
        
        assert sqrt_px96 > quotient, "Price underflow"
        return sqrt_px96 - quotient


def get_next_sqrt_price_from_input(
    sqrt_px96: int, liquidity: int, amount_in: int, zero_for_one: bool
) -> int:
    """
    Gets the next sqrt price given an input amount of token0 or token1
    
    Args:
        sqrt_px96: The starting price
        liquidity: The amount of usable liquidity
        amount_in: How much of token0 or token1 is being swapped in
        zero_for_one: Whether the amount in is token0 or token1
        
    Returns:
        sqrtQX96: The price after adding the input amount
    """
    assert sqrt_px96 > 0, "Price must be positive"
    assert liquidity > 0, "Liquidity must be positive"
    
    if zero_for_one:
        return get_next_sqrt_price_from_amount0_rounding_up(sqrt_px96, liquidity, amount_in, True)
    else:
        return get_next_sqrt_price_from_amount1_rounding_down(sqrt_px96, liquidity, amount_in, True)


def get_next_sqrt_price_from_output(
    sqrt_px96: int, liquidity: int, amount_out: int, zero_for_one: bool
) -> int:
    """
    Gets the next sqrt price given an output amount of token0 or token1
    
    Args:
        sqrt_px96: The starting price
        liquidity: The amount of usable liquidity
        amount_out: How much of token0 or token1 is being swapped out
        zero_for_one: Whether the amount out is token0 or token1
        
    Returns:
        sqrtQX96: The price after removing the output amount
    """
    assert sqrt_px96 > 0, "Price must be positive"
    assert liquidity > 0, "Liquidity must be positive"
    
    if zero_for_one:
        return get_next_sqrt_price_from_amount1_rounding_down(sqrt_px96, liquidity, amount_out, False)
    else:
        return get_next_sqrt_price_from_amount0_rounding_up(sqrt_px96, liquidity, amount_out, False)


def get_amount0_delta(
    sqrt_ratio_ax96: int, sqrt_ratio_bx96: int, liquidity: int, round_up: bool
) -> int:
    """
    Gets the amount0 delta between two prices
    Calculates liquidity / sqrt(lower) - liquidity / sqrt(upper)
    
    Args:
        sqrt_ratio_ax96: A sqrt price
        sqrt_ratio_bx96: Another sqrt price
        liquidity: The amount of usable liquidity
        round_up: Whether to round the amount up or down
        
    Returns:
        amount0: Amount of token0 required to cover a position of size liquidity between the two prices
    """
    if sqrt_ratio_ax96 > sqrt_ratio_bx96:
        sqrt_ratio_ax96, sqrt_ratio_bx96 = sqrt_ratio_bx96, sqrt_ratio_ax96
    
    numerator1 = liquidity << 96
    numerator2 = sqrt_ratio_bx96 - sqrt_ratio_ax96
    
    assert sqrt_ratio_ax96 > 0, "sqrt_ratio_ax96 must be positive"
    
    if round_up:
        return _div_rounding_up(
            mul_div_rounding_up(numerator1, numerator2, sqrt_ratio_bx96),
            sqrt_ratio_ax96
        )
    else:
        return mul_div(numerator1, numerator2, sqrt_ratio_bx96) // sqrt_ratio_ax96


def get_amount1_delta(
    sqrt_ratio_ax96: int, sqrt_ratio_bx96: int, liquidity: int, round_up: bool
) -> int:
    """
    Gets the amount1 delta between two prices
    Calculates liquidity * (sqrt(upper) - sqrt(lower))
    
    Args:
        sqrt_ratio_ax96: A sqrt price
        sqrt_ratio_bx96: Another sqrt price
        liquidity: The amount of usable liquidity
        round_up: Whether to round the amount up or down
        
    Returns:
        amount1: Amount of token1 required to cover a position of size liquidity between the two prices
    """
    if sqrt_ratio_ax96 > sqrt_ratio_bx96:
        sqrt_ratio_ax96, sqrt_ratio_bx96 = sqrt_ratio_bx96, sqrt_ratio_ax96
    
    if round_up:
        return mul_div_rounding_up(liquidity, sqrt_ratio_bx96 - sqrt_ratio_ax96, Q96)
    else:
        return mul_div(liquidity, sqrt_ratio_bx96 - sqrt_ratio_ax96, Q96)

