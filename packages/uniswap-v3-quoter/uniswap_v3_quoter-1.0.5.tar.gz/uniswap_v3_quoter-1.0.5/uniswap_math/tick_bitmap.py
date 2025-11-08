"""
TickBitmap Library
Ported from Solidity: v3-core/contracts/libraries/TickBitmap.sol

Stores a packed mapping of tick index to its initialized state
The mapping uses int16 for keys since ticks are represented as int24 and there are 256 (2^8) values per word
"""


def _most_significant_bit(x: int) -> int:
    """Find the most significant bit of a uint256"""
    if x == 0:
        return 0
    
    msb = 0
    if x >= 0x100000000000000000000000000000000:
        x >>= 128
        msb += 128
    if x >= 0x10000000000000000:
        x >>= 64
        msb += 64
    if x >= 0x100000000:
        x >>= 32
        msb += 32
    if x >= 0x10000:
        x >>= 16
        msb += 16
    if x >= 0x100:
        x >>= 8
        msb += 8
    if x >= 0x10:
        x >>= 4
        msb += 4
    if x >= 0x4:
        x >>= 2
        msb += 2
    if x >= 0x2:
        msb += 1
    
    return msb


def _least_significant_bit(x: int) -> int:
    """Find the least significant bit of a uint256"""
    if x == 0:
        return 0
    
    # Find the position of the least significant 1 bit
    lsb = 0
    if x & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF == 0:
        lsb += 128
        x >>= 128
    if x & 0xFFFFFFFFFFFFFFFF == 0:
        lsb += 64
        x >>= 64
    if x & 0xFFFFFFFF == 0:
        lsb += 32
        x >>= 32
    if x & 0xFFFF == 0:
        lsb += 16
        x >>= 16
    if x & 0xFF == 0:
        lsb += 8
        x >>= 8
    if x & 0xF == 0:
        lsb += 4
        x >>= 4
    if x & 0x3 == 0:
        lsb += 2
        x >>= 2
    if x & 0x1 == 0:
        lsb += 1
    
    return lsb


def next_initialized_tick_within_one_word(
    tick_bitmap: dict[int, int],
    tick: int,
    tick_spacing: int,
    lte: bool,
) -> tuple[int, bool]:
    """
    Returns the next initialized tick contained in the same word (or adjacent word) as the tick that is either
    to the left (less than or equal to) or right (greater than) of the given tick
    
    Args:
        tick_bitmap: The mapping in which to compute the next initialized tick
        tick: The starting tick
        tick_spacing: The spacing between usable ticks
        lte: Whether to search for the next initialized tick to the left (less than or equal to the starting tick)
        
    Returns:
        Tuple of (next, initialized):
        - next: The next initialized or uninitialized tick up to 256 ticks away from the current tick
        - initialized: Whether the next tick is initialized
    """
    compressed = tick // tick_spacing
    if tick < 0 and tick % tick_spacing != 0:
        compressed -= 1  # Round towards negative infinity
    
    if lte:
        word_pos = compressed >> 8
        bit_pos = compressed & 0xFF
        
        # All the 1s at or to the right of the current bitPos
        mask = ((1 << bit_pos) - 1) + (1 << bit_pos)
        masked = tick_bitmap.get(word_pos, 0) & mask
        
        # If there are no initialized ticks to the right of or at the current tick, return rightmost in the word
        initialized = masked != 0
        
        # overflow/underflow is possible, but prevented externally by limiting both tickSpacing and tick
        if initialized:
            next_tick = (compressed - (bit_pos - _most_significant_bit(masked))) * tick_spacing
        else:
            next_tick = (compressed - bit_pos) * tick_spacing
    else:
        # Start from the word of the next tick, since the current tick state doesn't matter
        word_pos = (compressed + 1) >> 8
        bit_pos = (compressed + 1) & 0xFF
        
        # All the 1s at or to the left of the bitPos
        mask = ~((1 << bit_pos) - 1)
        masked = tick_bitmap.get(word_pos, 0) & mask
        
        # If there are no initialized ticks to the left of the current tick, return leftmost in the word
        initialized = masked != 0
        
        # overflow/underflow is possible, but prevented externally by limiting both tickSpacing and tick
        if initialized:
            next_tick = (compressed + 1 + (_least_significant_bit(masked) - bit_pos)) * tick_spacing
        else:
            next_tick = (compressed + 1 + (255 - bit_pos)) * tick_spacing
    
    return next_tick, initialized

