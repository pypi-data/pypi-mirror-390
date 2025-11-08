"""
TickMath Library
Ported from Solidity: v3-core/contracts/libraries/TickMath.sol

Computes sqrt price for ticks of size 1.0001, i.e. sqrt(1.0001^tick) as fixed point Q64.96 numbers.
Supports prices between 2**-128 and 2**128
"""

# The minimum tick that may be passed to #getSqrtRatioAtTick computed from log base 1.0001 of 2**-128
MIN_TICK = -887272

# The maximum tick that may be passed to #getSqrtRatioAtTick computed from log base 1.0001 of 2**128
MAX_TICK = 887272

# The minimum value that can be returned from #getSqrtRatioAtTick. Equivalent to getSqrtRatioAtTick(MIN_TICK)
MIN_SQRT_RATIO = 4295128739

# The maximum value that can be returned from #getSqrtRatioAtTick. Equivalent to getSqrtRatioAtTick(MAX_TICK)
MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342


def get_sqrt_ratio_at_tick(tick: int) -> int:
    """
    Calculates sqrt(1.0001^tick) * 2^96
    
    Args:
        tick: The input tick for the above formula
        
    Returns:
        sqrtPriceX96: A Fixed point Q64.96 number representing the sqrt of the ratio
                      of the two assets (token1/token0) at the given tick
    """
    abs_tick = abs(tick)
    assert abs_tick <= MAX_TICK, f"Tick {tick} out of bounds"
    
    # Precomputed values of sqrt(1.0001^(2^n)) * 2^128 for n = 0..19
    ratio = 0xfffcb933bd6fad37aa2d162d1a594001 if (abs_tick & 0x1) else 0x100000000000000000000000000000000
    
    if abs_tick & 0x2:
        ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128
    if abs_tick & 0x4:
        ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128
    if abs_tick & 0x8:
        ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0) >> 128
    if abs_tick & 0x10:
        ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644) >> 128
    if abs_tick & 0x20:
        ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0) >> 128
    if abs_tick & 0x40:
        ratio = (ratio * 0xff2ea16466c96a3843ec78b326b52861) >> 128
    if abs_tick & 0x80:
        ratio = (ratio * 0xfe5dee046a99a2a811c461f1969c3053) >> 128
    if abs_tick & 0x100:
        ratio = (ratio * 0xfcbe86c7900a88aedcffc83b479aa3a4) >> 128
    if abs_tick & 0x200:
        ratio = (ratio * 0xf987a7253ac413176f2b074cf7815e54) >> 128
    if abs_tick & 0x400:
        ratio = (ratio * 0xf3392b0822b70005940c7a398e4b70f3) >> 128
    if abs_tick & 0x800:
        ratio = (ratio * 0xe7159475a2c29b7443b29c7fa6e889d9) >> 128
    if abs_tick & 0x1000:
        ratio = (ratio * 0xd097f3bdfd2022b8845ad8f792aa5825) >> 128
    if abs_tick & 0x2000:
        ratio = (ratio * 0xa9f746462d870fdf8a65dc1f90e061e5) >> 128
    if abs_tick & 0x4000:
        ratio = (ratio * 0x70d869a156d2a1b890bb3df62baf32f7) >> 128
    if abs_tick & 0x8000:
        ratio = (ratio * 0x31be135f97d08fd981231505542fcfa6) >> 128
    if abs_tick & 0x10000:
        ratio = (ratio * 0x9aa508b5b7a84e1c677de54f3e99bc9) >> 128
    if abs_tick & 0x20000:
        ratio = (ratio * 0x5d6af8dedb81196699c329225ee604) >> 128
    if abs_tick & 0x40000:
        ratio = (ratio * 0x2216e584f5fa1ea926041bedfe98) >> 128
    if abs_tick & 0x80000:
        ratio = (ratio * 0x48a170391f7dc42444e8fa2) >> 128
    
    if tick > 0:
        ratio = ((1 << 256) - 1) // ratio
    
    # Downcast from Q128.128 to Q128.96
    # We round up in the division so getTickAtSqrtRatio of the output price is always consistent
    sqrt_price_x96 = (ratio >> 32) + (0 if ratio % (1 << 32) == 0 else 1)
    
    return sqrt_price_x96


def get_tick_at_sqrt_ratio(sqrt_price_x96: int) -> int:
    """
    Calculates the greatest tick value such that getRatioAtTick(tick) <= ratio
    
    Args:
        sqrt_price_x96: The sqrt ratio for which to compute the tick as a Q64.96
        
    Returns:
        tick: The greatest tick for which the ratio is less than or equal to the input ratio
    """
    assert MIN_SQRT_RATIO <= sqrt_price_x96 < MAX_SQRT_RATIO, "sqrt_price_x96 out of bounds"
    
    ratio = sqrt_price_x96 << 32
    
    # Compute msb (most significant bit) of ratio
    r = ratio
    msb = 0
    
    # Binary search for MSB
    f = (r > 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) << 7
    msb |= f
    r >>= f
    
    f = (r > 0xFFFFFFFFFFFFFFFF) << 6
    msb |= f
    r >>= f
    
    f = (r > 0xFFFFFFFF) << 5
    msb |= f
    r >>= f
    
    f = (r > 0xFFFF) << 4
    msb |= f
    r >>= f
    
    f = (r > 0xFF) << 3
    msb |= f
    r >>= f
    
    f = (r > 0xF) << 2
    msb |= f
    r >>= f
    
    f = (r > 0x3) << 1
    msb |= f
    r >>= f
    
    f = r > 0x1
    msb |= f
    
    # Compute log_2 in Q128.128
    if msb >= 128:
        r = ratio >> (msb - 127)
    else:
        r = ratio << (127 - msb)
    
    log_2 = (msb - 128) << 64
    
    # Refine log_2 estimate with Taylor series
    for i in range(14):
        r = (r * r) >> 127
        f = r >> 128
        log_2 |= f << (63 - i)
        r >>= f
    
    # Convert log_2 to log_sqrt10001
    log_sqrt10001 = log_2 * 255738958999603826347141  # 128.128 number
    
    # Compute tick range
    tick_low = (log_sqrt10001 - 3402992956809132418596140100660247210) >> 128
    tick_hi = (log_sqrt10001 + 291339464771989622907027621153398088495) >> 128
    
    # Handle sign conversion for Python
    if tick_low >= (1 << 23):  # int24 negative range
        tick_low -= (1 << 24)
    if tick_hi >= (1 << 23):
        tick_hi -= (1 << 24)
    
    if tick_low == tick_hi:
        return tick_low
    else:
        return tick_hi if get_sqrt_ratio_at_tick(tick_hi) <= sqrt_price_x96 else tick_low

