"""
Pool State Management
Stores the current state of a Uniswap V3 pool in memory
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TickInfo:
    """Information stored for each initialized tick"""
    liquidity_gross: int = 0  # uint128
    liquidity_net: int = 0  # int128
    fee_growth_outside_0_x128: int = 0  # uint256
    fee_growth_outside_1_x128: int = 0  # uint256
    tick_cumulative_outside: int = 0  # int56
    seconds_per_liquidity_outside_x128: int = 0  # uint160
    seconds_outside: int = 0  # uint32
    initialized: bool = False


@dataclass
class PoolState:
    """
    State of a Uniswap V3 Pool
    Stores all necessary information to perform quote calculations locally
    """
    # Pool address
    address: str
    
    # Token addresses
    token0: str
    token1: str
    
    # Immutable pool parameters
    fee: int  # uint24 - fee in hundredths of a bip (e.g., 3000 = 0.3%)
    tick_spacing: int  # int24
    
    # Current pool state (from slot0)
    sqrt_price_x96: int = 0  # uint160
    tick: int = 0  # int24
    observation_index: int = 0  # uint16
    observation_cardinality: int = 0  # uint16
    observation_cardinality_next: int = 0  # uint16
    fee_protocol: int = 0  # uint8
    unlocked: bool = True
    
    # Current liquidity
    liquidity: int = 0  # uint128
    
    # Fee growth global
    fee_growth_global_0_x128: int = 0  # uint256
    fee_growth_global_1_x128: int = 0  # uint256
    
    # Tick data - only store initialized ticks
    ticks: Dict[int, TickInfo] = field(default_factory=dict)
    
    # Tick bitmap - mapping of int16 -> uint256
    tick_bitmap: Dict[int, int] = field(default_factory=dict)
    
    # Metadata
    last_update_block: int = 0
    last_update_timestamp: float = 0.0
    
    def get_tick(self, tick: int) -> Optional[TickInfo]:
        """Get tick info for a specific tick"""
        return self.ticks.get(tick)
    
    def set_tick(self, tick: int, tick_info: TickInfo):
        """Set tick info for a specific tick"""
        self.ticks[tick] = tick_info
    
    def get_tick_bitmap_word(self, word_pos: int) -> int:
        """Get a word from the tick bitmap"""
        return self.tick_bitmap.get(word_pos, 0)
    
    def set_tick_bitmap_word(self, word_pos: int, value: int):
        """Set a word in the tick bitmap"""
        self.tick_bitmap[word_pos] = value
    
    def __str__(self) -> str:
        return (
            f"PoolState(address={self.address}, "
            f"token0={self.token0}, token1={self.token1}, "
            f"fee={self.fee}, tick={self.tick}, "
            f"sqrt_price_x96={self.sqrt_price_x96}, "
            f"liquidity={self.liquidity})"
        )

