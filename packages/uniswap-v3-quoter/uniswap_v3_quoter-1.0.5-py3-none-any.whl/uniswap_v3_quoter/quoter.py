"""
Uniswap V3 Quoter
Main quoter implementation for calculating swap amounts without executing swaps
"""

from typing import Optional, Tuple
from web3 import Web3

from .uniswap_math import (
    MIN_SQRT_RATIO,
    MAX_SQRT_RATIO,
    get_tick_at_sqrt_ratio,
    compute_swap_step,
    next_initialized_tick_within_one_word,
    add_delta,
)
from .state import PoolState, StateFetcher


class QuoterV3:
    """
    Uniswap V3 Quoter implementation in Python
    Provides local quote calculations without on-chain calls
    """
    
    def __init__(
        self,
        w3: Web3,
        state_fetcher: Optional[StateFetcher] = None,
    ):
        """
        Initialize QuoterV3
        
        Args:
            w3: Web3 instance
            state_fetcher: StateFetcher instance (will create one if not provided)
        """
        self.w3 = w3
        self.state_fetcher = state_fetcher or StateFetcher(w3)
    
    def quote_exact_input_single(
        self,
        pool_address: str,
        zero_for_one: bool,
        amount_in: int,
        sqrt_price_limit_x96: int = 0,
    ) -> int:
        """
        Quote exact input for a single pool swap
        
        Args:
            pool_address: Address of the Uniswap V3 pool
            zero_for_one: True if swapping token0 for token1, False otherwise
            amount_in: Amount of input token
            sqrt_price_limit_x96: Price limit (0 for no limit)
            
        Returns:
            amount_out: Expected output amount
        """
        # Get pool state from cache
        pool_state = self.state_fetcher.get_pool_state(pool_address)
        if pool_state is None:
            raise ValueError(f"Pool state not found for {pool_address}. Fetch state first.")
        
        # Set price limit if not specified
        if sqrt_price_limit_x96 == 0:
            sqrt_price_limit_x96 = (
                MIN_SQRT_RATIO + 1 if zero_for_one else MAX_SQRT_RATIO - 1
            )
        
        # Validate price limit
        if zero_for_one:
            assert sqrt_price_limit_x96 < pool_state.sqrt_price_x96, "Price limit too high"
            assert sqrt_price_limit_x96 > MIN_SQRT_RATIO, "Price limit too low"
        else:
            assert sqrt_price_limit_x96 > pool_state.sqrt_price_x96, "Price limit too low"
            assert sqrt_price_limit_x96 < MAX_SQRT_RATIO, "Price limit too high"
        
        # Initialize swap state
        amount_specified_remaining = amount_in
        amount_calculated = 0
        sqrt_price_x96 = pool_state.sqrt_price_x96
        tick = pool_state.tick
        liquidity = pool_state.liquidity
        
        # Main swap loop
        while amount_specified_remaining > 0 and sqrt_price_x96 != sqrt_price_limit_x96:
            # Find next initialized tick
            tick_next, initialized = next_initialized_tick_within_one_word(
                pool_state.tick_bitmap,
                tick,
                pool_state.tick_spacing,
                zero_for_one,
            )
            
            # Ensure tick is within bounds
            from uniswap_math.tick_math import MIN_TICK, MAX_TICK
            if tick_next < MIN_TICK:
                tick_next = MIN_TICK
            elif tick_next > MAX_TICK:
                tick_next = MAX_TICK
            
            # Get sqrt price at next tick
            from uniswap_math import get_sqrt_ratio_at_tick
            sqrt_price_next_x96 = get_sqrt_ratio_at_tick(tick_next)
            
            # Compute swap step
            target_price = (
                sqrt_price_next_x96 if (
                    (sqrt_price_next_x96 < sqrt_price_limit_x96) if zero_for_one
                    else (sqrt_price_next_x96 > sqrt_price_limit_x96)
                ) else sqrt_price_limit_x96
            )
            
            sqrt_price_x96, amount_in_step, amount_out_step, fee_amount = compute_swap_step(
                sqrt_price_x96,
                target_price,
                liquidity,
                amount_specified_remaining,
                pool_state.fee,
            )
            
            # Update amounts
            amount_specified_remaining -= (amount_in_step + fee_amount)
            amount_calculated += amount_out_step
            
            # If we reached the next tick, cross it
            if sqrt_price_x96 == sqrt_price_next_x96:
                if initialized:
                    # Get tick info
                    tick_info = pool_state.get_tick(tick_next)
                    if tick_info and tick_info.initialized:
                        liquidity_net = tick_info.liquidity_net
                        
                        # If we're moving leftward, we interpret liquidityNet as opposite sign
                        if zero_for_one:
                            liquidity_net = -liquidity_net
                        
                        # Update liquidity
                        liquidity = add_delta(liquidity, liquidity_net)
                
                # Update tick
                tick = tick_next - 1 if zero_for_one else tick_next
            elif sqrt_price_x96 != pool_state.sqrt_price_x96:
                # Recompute tick if price changed but didn't cross
                tick = get_tick_at_sqrt_ratio(sqrt_price_x96)
        
        return amount_calculated
    
    def quote_exact_input_single_params(
        self,
        token_in: str,
        token_out: str,
        fee: int,
        amount_in: int,
        sqrt_price_limit_x96: int = 0,
    ) -> int:
        """
        Quote exact input for a single pool swap using token addresses
        
        Args:
            token_in: Address of input token
            token_out: Address of output token  
            fee: Pool fee tier
            amount_in: Amount of input token
            sqrt_price_limit_x96: Price limit (0 for no limit)
            
        Returns:
            amount_out: Expected output amount
        """
        # Find pool with matching tokens and fee
        # Note: In production, you'd compute pool address or look it up
        # For now, assume pool_address is provided separately
        raise NotImplementedError(
            "Use compute_pool_address() or provide pool_address directly"
        )
    
    def quote_exact_input(
        self,
        path: bytes,
        amount_in: int,
    ) -> int:
        """
        Quote exact input for a multi-hop swap
        
        Args:
            path: Encoded path (token0, fee0, token1, fee1, token2, ...)
            amount_in: Amount of first token
            
        Returns:
            amount_out: Expected final output amount
        """
        # Parse path
        # Path format: address(20) + uint24(3) + address(20) + ...
        if len(path) < 43:  # Minimum: address + fee + address
            raise ValueError("Invalid path length")
        
        current_amount = amount_in
        offset = 0
        
        while offset < len(path):
            # Extract token_in (20 bytes)
            token_in = path[offset:offset + 20]
            offset += 20
            
            if offset >= len(path):
                break
            
            # Extract fee (3 bytes)
            fee = int.from_bytes(path[offset:offset + 3], byteorder='big')
            offset += 3
            
            # Extract token_out (20 bytes)
            if offset + 20 > len(path):
                raise ValueError("Invalid path format")
            token_out = path[offset:offset + 20]
            
            # Determine zero_for_one
            zero_for_one = token_in < token_out
            
            # Compute pool address (simplified - in production use proper address computation)
            # For now, this requires pool to be fetched beforehand
            pool_address = self._compute_pool_address(token_in, token_out, fee)
            
            # Quote this hop
            current_amount = self.quote_exact_input_single(
                pool_address,
                zero_for_one,
                current_amount,
                0,
            )
        
        return current_amount
    
    def _compute_pool_address(
        self,
        token_in: bytes,
        token_out: bytes,
        fee: int,
    ) -> str:
        """
        Compute pool address from tokens and fee
        
        Note: This is a simplified version. In production, use CREATE2 address computation
        with the actual factory address and init code hash.
        """
        # Sort tokens
        token0, token1 = (token_in, token_out) if token_in < token_out else (token_out, token_in)
        
        # In production, compute using:
        # keccak256(abi.encodePacked(
        #     hex'ff',
        #     factory,
        #     keccak256(abi.encode(token0, token1, fee)),
        #     POOL_INIT_CODE_HASH
        # ))
        
        raise NotImplementedError("Pool address computation not implemented")
    
    def add_pool(
        self,
        pool_address: str,
        fetch_tick_range: Optional[Tuple[int, int]] = None,
    ) -> PoolState:
        """
        Add a pool to the quoter (fetch and cache its state)
        
        Args:
            pool_address: Address of the pool
            fetch_tick_range: Optional (min_tick, max_tick) to pre-fetch
            
        Returns:
            Fetched PoolState
        """
        return self.state_fetcher.fetch_pool_state(pool_address, fetch_tick_range)
    
    def update_pool(self, pool_address: str) -> PoolState:
        """
        Update a pool's state
        
        Args:
            pool_address: Address of the pool
            
        Returns:
            Updated PoolState
        """
        return self.state_fetcher.update_pool_state(pool_address)
    
    def get_pool(self, pool_address: str) -> Optional[PoolState]:
        """
        Get cached pool state
        
        Args:
            pool_address: Address of the pool
            
        Returns:
            PoolState if cached, None otherwise
        """
        return self.state_fetcher.get_pool_state(pool_address)

