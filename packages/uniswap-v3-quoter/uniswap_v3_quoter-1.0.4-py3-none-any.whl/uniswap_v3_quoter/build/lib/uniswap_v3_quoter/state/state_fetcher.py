"""
State Fetcher
Fetches pool state from BSC using web3.py and multicall
"""

import time
import threading
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from web3 import Web3
from eth_abi import decode

from .pool_state import PoolState, TickInfo

if TYPE_CHECKING:
    from .ws_subscriber import WebSocketSubscriber


# Uniswap V3 Pool ABI (only the functions we need)
POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"name": "sqrtPriceX96", "type": "uint160"},
            {"name": "tick", "type": "int24"},
            {"name": "observationIndex", "type": "uint16"},
            {"name": "observationCardinality", "type": "uint16"},
            {"name": "observationCardinalityNext", "type": "uint16"},
            {"name": "feeProtocol", "type": "uint8"},
            {"name": "unlocked", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "fee",
        "outputs": [{"name": "", "type": "uint24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "tickSpacing",
        "outputs": [{"name": "", "type": "int24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "", "type": "int24"}],
        "name": "ticks",
        "outputs": [
            {"name": "liquidityGross", "type": "uint128"},
            {"name": "liquidityNet", "type": "int128"},
            {"name": "feeGrowthOutside0X128", "type": "uint256"},
            {"name": "feeGrowthOutside1X128", "type": "uint256"},
            {"name": "tickCumulativeOutside", "type": "int56"},
            {"name": "secondsPerLiquidityOutsideX128", "type": "uint160"},
            {"name": "secondsOutside", "type": "uint32"},
            {"name": "initialized", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "", "type": "int16"}],
        "name": "tickBitmap",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal0X128",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal1X128",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Multicall3 ABI
MULTICALL3_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "target", "type": "address"},
                    {"name": "callData", "type": "bytes"},
                ],
                "name": "calls",
                "type": "tuple[]",
            }
        ],
        "name": "aggregate",
        "outputs": [
            {"name": "blockNumber", "type": "uint256"},
            {"name": "returnData", "type": "bytes[]"},
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"name": "target", "type": "address"},
                    {"name": "allowFailure", "type": "bool"},
                    {"name": "callData", "type": "bytes"},
                ],
                "name": "calls",
                "type": "tuple[]",
            }
        ],
        "name": "tryAggregate",
        "outputs": [
            {
                "components": [
                    {"name": "success", "type": "bool"},
                    {"name": "returnData", "type": "bytes"},
                ],
                "name": "returnData",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "payable",
        "type": "function",
    },
]


def _decode_slot0_manual(raw_data: bytes) -> Tuple:
    """
    Manually decode slot0 data to avoid padding validation issues with PancakeSwap V3
    
    Args:
        raw_data: Raw bytes from slot0() call
        
    Returns:
        Tuple of (sqrtPriceX96, tick, observationIndex, observationCardinality,
                  observationCardinalityNext, feeProtocol, unlocked)
    """
    # Each field is 32 bytes in ABI encoding
    sqrtPriceX96 = int.from_bytes(raw_data[0:32], 'big')
    
    # int24 tick
    tick_raw = int.from_bytes(raw_data[32:64], 'big')
    if tick_raw >= (1 << 23):  # int24 negative range
        tick = tick_raw - (1 << 24)
    else:
        tick = tick_raw
    
    # uint16 fields - mask to 16 bits to handle padding
    observationIndex = int.from_bytes(raw_data[64:96], 'big') & 0xFFFF
    observationCardinality = int.from_bytes(raw_data[96:128], 'big') & 0xFFFF
    observationCardinalityNext = int.from_bytes(raw_data[128:160], 'big') & 0xFFFF
    
    # uint8 feeProtocol - mask to 8 bits
    feeProtocol = int.from_bytes(raw_data[160:192], 'big') & 0xFF
    
    # bool unlocked
    unlocked = bool(int.from_bytes(raw_data[192:224], 'big'))
    
    return (
        sqrtPriceX96,
        tick,
        observationIndex,
        observationCardinality,
        observationCardinalityNext,
        feeProtocol,
        unlocked,
    )


class StateFetcher:
    """
    Fetches and maintains pool state from blockchain
    Uses multicall to batch RPC calls for efficiency
    """
    
    def __init__(
        self,
        w3: Web3,
        multicall_address: str = "0xcA11bde05977b3631167028862bE2a173976CA11",
        ws_subscriber: Optional['WebSocketSubscriber'] = None,
    ):
        """
        Initialize StateFetcher
        
        Args:
            w3: Web3 instance connected to BSC
            multicall_address: Address of Multicall3 contract on BSC
            ws_subscriber: Optional WebSocketSubscriber for realtime updates
        """
        self.w3 = w3
        self.multicall = w3.eth.contract(
            address=Web3.to_checksum_address(multicall_address),
            abi=MULTICALL3_ABI,
        )
        
        # Cache of pool states
        self.pools: Dict[str, PoolState] = {}
        
        # Background update thread
        self._update_thread: Optional[threading.Thread] = None
        self._stop_update = threading.Event()
        self._update_lock = threading.Lock()
        
        # WebSocket subscriber integration
        self.ws_subscriber = ws_subscriber
        if self.ws_subscriber:
            # Set callback to update pool states from Swap events
            self.ws_subscriber.set_callback(self.update_from_swap_event)
    
    def fetch_pool_state(
        self,
        pool_address: str,
        fetch_tick_range: Optional[Tuple[int, int]] = None,
    ) -> PoolState:
        """
        Fetch complete pool state from blockchain
        
        Args:
            pool_address: Address of the Uniswap V3 pool
            fetch_tick_range: Optional (min_tick, max_tick) to fetch tick data for
            
        Returns:
            PoolState object with current pool state
        """
        pool_address = Web3.to_checksum_address(pool_address)
        pool_contract = self.w3.eth.contract(address=pool_address, abi=POOL_ABI)
        
        # Prepare multicall for basic pool data and measure call time
        import time
        calls = [
            (pool_address, pool_contract.encode_abi("slot0")),
            (pool_address, pool_contract.encode_abi("liquidity")),
            (pool_address, pool_contract.encode_abi("fee")),
            (pool_address, pool_contract.encode_abi("tickSpacing")),
            (pool_address, pool_contract.encode_abi("token0")),
            (pool_address, pool_contract.encode_abi("token1")),
            (pool_address, pool_contract.encode_abi("feeGrowthGlobal0X128")),
            (pool_address, pool_contract.encode_abi("feeGrowthGlobal1X128")),
        ]
        call_start_time = time.time()
        print(f"Starting multicall at {call_start_time}")
        
        # Execute multicall
        block_number, return_data = self.multicall.functions.aggregate(calls).call()
        
        # Decode results - Use manual decoding for slot0 to avoid padding issues
        slot0_data = _decode_slot0_manual(return_data[0])
        liquidity = decode(["uint128"], return_data[1])[0]
        fee = decode(["uint24"], return_data[2])[0]
        tick_spacing = decode(["int24"], return_data[3])[0]
        token0 = decode(["address"], return_data[4])[0]
        token1 = decode(["address"], return_data[5])[0]
        fee_growth_global_0 = decode(["uint256"], return_data[6])[0]
        fee_growth_global_1 = decode(["uint256"], return_data[7])[0]
        
        # Tick already converted in manual decode
        tick = slot0_data[1]
        
        # Convert int24 tick_spacing to Python int
        if tick_spacing >= (1 << 23):
            tick_spacing -= (1 << 24)
        
        # Create pool state
        pool_state = PoolState(
            address=pool_address,
            token0=token0,
            token1=token1,
            fee=fee,
            tick_spacing=tick_spacing,
            sqrt_price_x96=slot0_data[0],
            tick=tick,
            observation_index=slot0_data[2],
            observation_cardinality=slot0_data[3],
            observation_cardinality_next=slot0_data[4],
            fee_protocol=slot0_data[5],
            unlocked=slot0_data[6],
            liquidity=liquidity,
            fee_growth_global_0_x128=fee_growth_global_0,
            fee_growth_global_1_x128=fee_growth_global_1,
            last_update_block=block_number,
            last_update_timestamp=time.time(),
        )
        
        # Optionally fetch tick data
        if fetch_tick_range:
            self._fetch_tick_data(pool_state, fetch_tick_range)
        
        # Cache the pool state
        with self._update_lock:
            self.pools[pool_address] = pool_state
        
        # Auto-subscribe to WebSocket if available
        if self.ws_subscriber:
            self.ws_subscriber.subscribe_pool(pool_address)
        
        return pool_state
    
    def _fetch_tick_data(self, pool_state: PoolState, tick_range: Tuple[int, int]):
        """
        Fetch tick data for a range of ticks
        
        Args:
            pool_state: Pool state to update
            tick_range: (min_tick, max_tick) range to fetch
        """
        pool_contract = self.w3.eth.contract(
            address=pool_state.address, abi=POOL_ABI
        )
        
        min_tick, max_tick = tick_range
        tick_spacing = pool_state.tick_spacing
        
        # Generate tick list (aligned to tick spacing)
        min_tick = (min_tick // tick_spacing) * tick_spacing
        max_tick = (max_tick // tick_spacing) * tick_spacing
        
        # Fetch tick bitmap for the range
        min_word = min_tick // tick_spacing >> 8
        max_word = max_tick // tick_spacing >> 8
        
        # Prepare multicall for tick bitmap
        bitmap_calls = []
        for word_pos in range(min_word, max_word + 1):
            bitmap_calls.append(
                (pool_state.address, pool_contract.encode_abi("tickBitmap", [word_pos]))
            )
        
        if bitmap_calls:
            _, bitmap_data = self.multicall.functions.aggregate(bitmap_calls).call()
            
            for i, word_pos in enumerate(range(min_word, max_word + 1)):
                bitmap_value = decode(["uint256"], bitmap_data[i])[0]
                pool_state.set_tick_bitmap_word(word_pos, bitmap_value)
    
    def update_pool_state(self, pool_address: str) -> PoolState:
        """
        Update existing pool state with latest data
        
        Args:
            pool_address: Address of the pool to update
            
        Returns:
            Updated PoolState
        """
        pool_address = Web3.to_checksum_address(pool_address)
        
        # If pool not in cache, fetch full state
        if pool_address not in self.pools:
            return self.fetch_pool_state(pool_address)
        
        pool_contract = self.w3.eth.contract(address=pool_address, abi=POOL_ABI)
        
        # Prepare multicall for quick update (slot0 + liquidity)
        calls = [
            (pool_address, pool_contract.encode_abi("slot0")),
            (pool_address, pool_contract.encode_abi("liquidity")),
        ]
        
        # Execute multicall
        import time
        start_time = time.time()
        block_number, return_data = self.multicall.functions.aggregate(calls).call()
        elapsed_time = (time.time() - start_time) * 1000  # ms
        print(f"[update_pool_state] Multicall took {elapsed_time:.2f}ms")
        
        # Decode results - Use manual decoding for slot0 to avoid padding issues
        slot0_data = _decode_slot0_manual(return_data[0])
        liquidity = decode(["uint128"], return_data[1])[0]
        
        # Tick already converted in manual decode
        tick = slot0_data[1]
        
        # Update pool state
        with self._update_lock:
            pool_state = self.pools[pool_address]
            pool_state.sqrt_price_x96 = slot0_data[0]
            pool_state.tick = tick
            pool_state.observation_index = slot0_data[2]
            pool_state.observation_cardinality = slot0_data[3]
            pool_state.observation_cardinality_next = slot0_data[4]
            pool_state.fee_protocol = slot0_data[5]
            pool_state.unlocked = slot0_data[6]
            pool_state.liquidity = liquidity
            pool_state.last_update_block = block_number
            pool_state.last_update_timestamp = time.time()
        
        return pool_state
    
    def get_pool_state(self, pool_address: str) -> Optional[PoolState]:
        """
        Get cached pool state
        
        Args:
            pool_address: Address of the pool
            
        Returns:
            PoolState if cached, None otherwise
        """
        pool_address = Web3.to_checksum_address(pool_address)
        with self._update_lock:
            return self.pools.get(pool_address)
    
    def start_background_update(
        self,
        pool_addresses: List[str],
        interval: float = 0.5,
    ):
        """
        Start background thread to continuously update pool states
        
        Args:
            pool_addresses: List of pool addresses to monitor
            interval: Update interval in seconds
        """
        if self._update_thread and self._update_thread.is_alive():
            raise RuntimeError("Background update already running")
        
        self._stop_update.clear()
        
        def update_loop():
            while not self._stop_update.is_set():
                try:
                    for pool_address in pool_addresses:
                        self.update_pool_state(pool_address)
                except Exception as e:
                    print(f"Error updating pool states: {e}")
                
                time.sleep(interval)
        
        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()
    
    def stop_background_update(self):
        """Stop background update thread"""
        if self._update_thread and self._update_thread.is_alive():
            self._stop_update.set()
            self._update_thread.join(timeout=5)
    
    def start_websocket(self):
        """
        Start WebSocket subscriber for realtime pool updates
        Requires ws_subscriber to be set during initialization
        """
        if not self.ws_subscriber:
            raise RuntimeError("No WebSocket subscriber configured. Pass ws_subscriber during initialization.")
        
        self.ws_subscriber.start()
    
    def stop_websocket(self):
        """
        Stop WebSocket subscriber
        """
        if self.ws_subscriber:
            self.ws_subscriber.stop()
    
    def update_from_swap_event(self, swap_event):
        """
        Update pool state from WebSocket Swap event
        This is called by WebSocket subscriber when new Swap events arrive
        
        Args:
            swap_event: SwapEventData from WebSocket subscriber
        """
        pool_address = Web3.to_checksum_address(swap_event.pool_address)
        
        with self._update_lock:
            pool_state = self.pools.get(pool_address)
            
            if pool_state is None:
                # Pool not in cache yet - skip update
                return
            
            # Update pool state with data from Swap event
            pool_state.sqrt_price_x96 = swap_event.sqrt_price_x96
            pool_state.tick = swap_event.tick
            pool_state.liquidity = swap_event.liquidity
            pool_state.last_update_block = swap_event.block_number
            pool_state.last_update_timestamp = swap_event.timestamp
