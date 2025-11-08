"""
SwapMath Library
Ported from Solidity: v3-core/contracts/libraries/SwapMath.sol

Computes the result of a swap within ticks
Contains methods for computing the result of a swap within a single tick price range
"""

from .full_math import mul_div, mul_div_rounding_up
from .sqrt_price_math import (
    get_amount0_delta,
    get_amount1_delta,
    get_next_sqrt_price_from_input,
    get_next_sqrt_price_from_output,
    Q96,
)


def compute_swap_step(
    sqrt_ratio_current_x96: int,
    sqrt_ratio_target_x96: int,
    liquidity: int,
    amount_remaining: int,
    fee_pips: int,
) -> tuple[int, int, int, int]:
    """
    Computes the result of swapping some amount in, or amount out, given the parameters of the swap
    
    The fee, plus the amount in, will never exceed the amount remaining if the swap's amountSpecified is positive
    
    Args:
        sqrt_ratio_current_x96: The current sqrt price of the pool
        sqrt_ratio_target_x96: The price that cannot be exceeded, from which the direction is inferred
        liquidity: The usable liquidity
        amount_remaining: How much input or output amount is remaining to be swapped in/out
        fee_pips: The fee taken from the input amount, expressed in hundredths of a bip
        
    Returns:
        Tuple of (sqrt_ratio_next_x96, amount_in, amount_out, fee_amount):
        - sqrt_ratio_next_x96: The price after swapping the amount in/out, not to exceed the price target
        - amount_in: The amount to be swapped in, of either token0 or token1, based on the direction
        - amount_out: The amount to be received, of either token0 or token1, based on the direction
        - fee_amount: The amount of input that will be taken as a fee
    """
    zero_for_one = sqrt_ratio_current_x96 >= sqrt_ratio_target_x96
    exact_in = amount_remaining >= 0
    
    if exact_in:
        amount_remaining_less_fee = mul_div(amount_remaining, 1_000_000 - fee_pips, 1_000_000)
        
        if zero_for_one:
            amount_in = get_amount0_delta(sqrt_ratio_target_x96, sqrt_ratio_current_x96, liquidity, True)
        else:
            amount_in = get_amount1_delta(sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, True)
        
        if amount_remaining_less_fee >= amount_in:
            sqrt_ratio_next_x96 = sqrt_ratio_target_x96
        else:
            sqrt_ratio_next_x96 = get_next_sqrt_price_from_input(
                sqrt_ratio_current_x96,
                liquidity,
                amount_remaining_less_fee,
                zero_for_one,
            )
    else:
        if zero_for_one:
            amount_out = get_amount1_delta(sqrt_ratio_target_x96, sqrt_ratio_current_x96, liquidity, False)
        else:
            amount_out = get_amount0_delta(sqrt_ratio_current_x96, sqrt_ratio_target_x96, liquidity, False)
        
        if -amount_remaining >= amount_out:
            sqrt_ratio_next_x96 = sqrt_ratio_target_x96
        else:
            sqrt_ratio_next_x96 = get_next_sqrt_price_from_output(
                sqrt_ratio_current_x96,
                liquidity,
                -amount_remaining,
                zero_for_one,
            )
    
    max_price_reached = sqrt_ratio_target_x96 == sqrt_ratio_next_x96
    
    # Get the input/output amounts
    if zero_for_one:
        if max_price_reached and exact_in:
            amount_in = amount_in  # Use previously computed amount_in
        else:
            amount_in = get_amount0_delta(sqrt_ratio_next_x96, sqrt_ratio_current_x96, liquidity, True)
        
        if max_price_reached and not exact_in:
            amount_out = amount_out  # Use previously computed amount_out
        else:
            amount_out = get_amount1_delta(sqrt_ratio_next_x96, sqrt_ratio_current_x96, liquidity, False)
    else:
        if max_price_reached and exact_in:
            amount_in = amount_in  # Use previously computed amount_in
        else:
            amount_in = get_amount1_delta(sqrt_ratio_current_x96, sqrt_ratio_next_x96, liquidity, True)
        
        if max_price_reached and not exact_in:
            amount_out = amount_out  # Use previously computed amount_out
        else:
            amount_out = get_amount0_delta(sqrt_ratio_current_x96, sqrt_ratio_next_x96, liquidity, False)
    
    # Cap the output amount to not exceed the remaining output amount
    if not exact_in and amount_out > -amount_remaining:
        amount_out = -amount_remaining
    
    if exact_in and sqrt_ratio_next_x96 != sqrt_ratio_target_x96:
        # We didn't reach the target, so take the remainder of the maximum input as fee
        fee_amount = amount_remaining - amount_in
    else:
        fee_amount = mul_div_rounding_up(amount_in, fee_pips, 1_000_000 - fee_pips)
    
    return sqrt_ratio_next_x96, amount_in, amount_out, fee_amount

