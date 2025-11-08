"""
WebSocket Subscriber for realtime pool state updates
Subscribes to Swap events and updates pool state with low latency
Uses Web3.py v7+ AsyncWeb3 with persistent WebSocket connection
"""

import time
import asyncio
import threading
import ssl
from typing import Callable, Dict, Optional, Set
from web3 import AsyncWeb3
from web3.providers import WebSocketProvider
from eth_abi import decode
from eth_utils import event_abi_to_log_topic
import json

# PancakeSwap V3 Swap event signature
# event Swap(
#     address indexed sender,
#     address indexed recipient,
#     int256 amount0,
#     int256 amount1,
#     uint160 sqrtPriceX96,
#     uint128 liquidity,
#     int24 tick,
#     uint128 protocolFeesToken0,
#     uint128 protocolFeesToken1
# )
SWAP_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "sender", "type": "address"},
        {"indexed": True, "name": "recipient", "type": "address"},
        {"indexed": False, "name": "amount0", "type": "int256"},
        {"indexed": False, "name": "amount1", "type": "int256"},
        {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"},
        {"indexed": False, "name": "liquidity", "type": "uint128"},
        {"indexed": False, "name": "tick", "type": "int24"},
        {"indexed": False, "name": "protocolFeesToken0", "type": "uint128"},
        {"indexed": False, "name": "protocolFeesToken1", "type": "uint128"},
    ],
    "name": "Swap",
    "type": "event",
}

# Calculate Swap event topic
SWAP_EVENT_TOPIC = event_abi_to_log_topic(SWAP_EVENT_ABI)


class SwapEventData:
    """Parsed Swap event data"""
    
    def __init__(
        self,
        pool_address: str,
        sqrt_price_x96: int,
        liquidity: int,
        tick: int,
        amount0: int,
        amount1: int,
        block_number: int,
        transaction_hash: str,
    ):
        self.pool_address = pool_address
        self.sqrt_price_x96 = sqrt_price_x96
        self.liquidity = liquidity
        self.tick = tick
        self.amount0 = amount0
        self.amount1 = amount1
        self.block_number = block_number
        self.transaction_hash = transaction_hash
        self.timestamp = time.time()


class WebSocketSubscriber:
    """
    WebSocket subscriber for pool Swap events
    Provides realtime state updates with low latency
    Uses AsyncWeb3 with persistent WebSocket connection
    """
    
    def __init__(
        self,
        wss_url: str,
        callback: Optional[Callable[[SwapEventData], None]] = None,
        reconnect_max_retries: int = 5,
        reconnect_delay: float = 1.0,
        reconnect_max_delay: float = 30.0,
        verify_ssl: bool = False,
    ):
        """
        Initialize WebSocket subscriber
        
        Args:
            wss_url: WebSocket URL (e.g., wss://bsc-mainnet.nodereal.io/ws/v1/...)
            callback: Optional callback function called when Swap event received
            reconnect_max_retries: Maximum reconnection attempts (0 = infinite)
            reconnect_delay: Initial delay between reconnections (seconds)
            reconnect_max_delay: Maximum delay between reconnections (seconds)
            verify_ssl: Whether to verify SSL certificates (default: False for QuickNode compatibility)
        """
        self.wss_url = wss_url
        self.callback = callback
        self.reconnect_max_retries = reconnect_max_retries
        self.reconnect_delay = reconnect_delay
        self.reconnect_max_delay = reconnect_max_delay
        self.verify_ssl = verify_ssl
        
        # Subscribed pools
        self.subscribed_pools: Set[str] = set()
        self.event_filters: Dict[str, any] = {}  # pool_address -> filter object
        
        # WebSocket state
        self.w3 = None
        self.provider = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Reconnection state
        self._reconnect_count = 0
        self._last_event_time = time.time()
    
    def set_callback(self, callback: Callable[[SwapEventData], None]):
        """
        Set or update the callback function
        
        Args:
            callback: Callback function to call when Swap event received
        """
        self.callback = callback
        
    def subscribe_pool(self, pool_address: str):
        """
        Subscribe to Swap events for a pool
        
        Args:
            pool_address: Address of the pool to subscribe
        """
        pool_address = AsyncWeb3.to_checksum_address(pool_address)
        
        if pool_address in self.subscribed_pools:
            print(f"[WS] Already subscribed to {pool_address}")
            return
        
        self.subscribed_pools.add(pool_address)
        
        # If already running, subscribe immediately
        if self._running and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._subscribe_pool_async(pool_address),
                self._loop
            )
        
        print(f"[WS] Added subscription for {pool_address}")
    
    def unsubscribe_pool(self, pool_address: str):
        """
        Unsubscribe from pool Swap events
        
        Args:
            pool_address: Address of the pool to unsubscribe
        """
        pool_address = AsyncWeb3.to_checksum_address(pool_address)
        
        if pool_address not in self.subscribed_pools:
            return
        
        # Unsubscribe if running
        if self._running and self._loop and pool_address in self.event_filters:
            asyncio.run_coroutine_threadsafe(
                self._unsubscribe_pool_async(pool_address),
                self._loop
            )
        
        self.subscribed_pools.discard(pool_address)
        self.event_filters.pop(pool_address, None)
        
        print(f"[WS] Unsubscribed from {pool_address}")
    
    def start(self):
        """Start WebSocket subscriber in background thread"""
        if self._running:
            print("[WS] Subscriber already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        print(f"[WS] Subscriber started for {len(self.subscribed_pools)} pool(s)")
    
    def stop(self):
        """Stop WebSocket subscriber"""
        if not self._running:
            return
        
        print("[WS] Stopping subscriber...")
        self._running = False
        
        if self._loop and self._loop.is_running():
            # Schedule cleanup
            asyncio.run_coroutine_threadsafe(self._cleanup(), self._loop)
        
        if self._thread:
            self._thread.join(timeout=5)
        
        print("[WS] Subscriber stopped")
    
    def _run_loop(self):
        """Run event loop in thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._connect_and_subscribe())
        except Exception as e:
            print(f"[WS] Event loop error: {e}")
        finally:
            self._loop.close()
    
    async def _connect_and_subscribe(self):
        """Connect to WebSocket and subscribe to pools"""
        while self._running:
            try:
                print(f"[WS] Connecting to {self.wss_url}...")
                
                # Create SSL context if needed
                websocket_kwargs = {}
                if not self.verify_ssl:
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    websocket_kwargs['ssl'] = ssl_context
                
                # Create WebSocket provider
                self.provider = WebSocketProvider(
                    self.wss_url,
                    websocket_kwargs=websocket_kwargs
                )
                
                # Connect the provider
                await self.provider.connect()
                print(f"[WS] Provider connected")
                
                # Create AsyncWeb3 instance
                self.w3 = AsyncWeb3(self.provider)
                
                # Verify connection
                is_connected = await self.w3.is_connected()
                if not is_connected:
                    raise ConnectionError("Failed to connect to WebSocket")
                
                # Get block number to confirm connection
                block_number = await self.w3.eth.block_number
                print(f"[WS] Connected! Latest block: {block_number}")
                self._reconnect_count = 0  # Reset on successful connection
                
                # Subscribe to all pools
                for pool_address in list(self.subscribed_pools):
                    await self._subscribe_pool_async(pool_address)
                
                # Keep connection alive and handle events
                await self._listen_loop()
                    
            except Exception as e:
                print(f"[WS] Connection error: {e}")
                await self._cleanup_connection()
                await self._handle_reconnect()
    
    async def _subscribe_pool_async(self, pool_address: str):
        """Subscribe to Swap events for a pool (async)"""
        try:
            if not self.w3:
                print(f"[WS] Not connected, cannot subscribe to {pool_address}")
                return
            
            # Create filter for Swap events
            # Ensure topic has 0x prefix
            topic_hex = SWAP_EVENT_TOPIC.hex() if isinstance(SWAP_EVENT_TOPIC, bytes) else SWAP_EVENT_TOPIC
            if not topic_hex.startswith('0x'):
                topic_hex = '0x' + topic_hex
            
            filter_params = {
                "address": pool_address,
                "topics": [topic_hex]
            }
            
            # Create event filter
            event_filter = await self.w3.eth.filter(filter_params)
            
            # Store the filter object (not just the ID)
            self.event_filters[pool_address] = event_filter
            filter_id = str(event_filter.filter_id)
            print(f"[WS] ✓ Subscribed to {pool_address} (ID: {filter_id[:8]}...)")
            
        except Exception as e:
            print(f"[WS] Failed to subscribe to {pool_address}: {e}")
    
    async def _unsubscribe_pool_async(self, pool_address: str):
        """Unsubscribe from pool (async)"""
        try:
            event_filter = self.event_filters.get(pool_address)
            if not event_filter or not self.w3:
                return
            
            # Uninstall filter
            await self.w3.eth.uninstall_filter(event_filter.filter_id)
            
            print(f"[WS] Unsubscribed from {pool_address}")
            
        except Exception as e:
            print(f"[WS] Failed to unsubscribe from {pool_address}: {e}")
    
    async def _listen_loop(self):
        """Listen for events"""
        print("[WS] Listening for Swap events...")
        
        while self._running and self.w3:
            try:
                # Check all subscribed pools for new events
                for pool_address, event_filter in list(self.event_filters.items()):
                    try:
                        # Get new entries from the filter
                        events = await event_filter.get_new_entries()
                        
                        for event in events:
                            await self._handle_event(event)
                            self._last_event_time = time.time()
                    
                    except Exception as e:
                        print(f"[WS] Error getting events for {pool_address}: {e}")
                
                # Small delay to avoid busy waiting
                await asyncio.sleep(0.1)
            
            except Exception as e:
                print(f"[WS] Listen loop error: {e}")
                break
        
        print("[WS] Listen loop ended")
    
    async def _handle_event(self, event):
        """Handle incoming Swap event"""
        try:
            # Parse event log
            swap_data = self._parse_swap_event(event)
            
            if swap_data and self.callback:
                # Call callback in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.callback, swap_data)
        
        except Exception as e:
            print(f"[WS] Error handling event: {e}")
    
    def _parse_swap_event(self, event) -> Optional[SwapEventData]:
        """
        Parse Swap event log
        
        Args:
            event: Event log from WebSocket
            
        Returns:
            SwapEventData or None if parsing fails
        """
        try:
            # Extract pool address
            pool_address = AsyncWeb3.to_checksum_address(event['address'])
            
            # Decode event data
            # Data contains: amount0, amount1, sqrtPriceX96, liquidity, tick, protocolFeesToken0, protocolFeesToken1
            # Handle both HexBytes and string
            event_data = event['data']
            if isinstance(event_data, bytes):
                data = event_data
            else:
                # It's a string with 0x prefix
                data = bytes.fromhex(event_data[2:] if event_data.startswith('0x') else event_data)
            
            decoded = decode(
                ['int256', 'int256', 'uint160', 'uint128', 'int24', 'uint128', 'uint128'],
                data
            )
            
            amount0 = decoded[0]
            amount1 = decoded[1]
            sqrt_price_x96 = decoded[2]
            liquidity = decoded[3]
            tick_raw = decoded[4]
            
            # Convert int24 tick to Python int
            if tick_raw >= (1 << 23):  # int24 negative range
                tick = tick_raw - (1 << 24)
            else:
                tick = tick_raw
            
            # Get block number and transaction hash
            block_number = event.get('blockNumber', 0)
            transaction_hash = event.get('transactionHash', '0x').hex() if isinstance(event.get('transactionHash'), bytes) else event.get('transactionHash', '0x')
            
            return SwapEventData(
                pool_address=pool_address,
                sqrt_price_x96=sqrt_price_x96,
                liquidity=liquidity,
                tick=tick,
                amount0=amount0,
                amount1=amount1,
                block_number=block_number,
                transaction_hash=transaction_hash,
            )
        
        except Exception as e:
            print(f"[WS] Failed to parse Swap event: {e}")
            return None
    
    async def _handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        if not self._running:
            return
        
        self._reconnect_count += 1
        
        if self.reconnect_max_retries > 0 and self._reconnect_count > self.reconnect_max_retries:
            print(f"[WS] Max reconnection attempts ({self.reconnect_max_retries}) reached. Giving up.")
            self._running = False
            return
        
        # Calculate delay with exponential backoff
        delay = min(
            self.reconnect_delay * (2 ** (self._reconnect_count - 1)),
            self.reconnect_max_delay
        )
        
        print(f"[WS] Reconnecting in {delay:.1f}s (attempt {self._reconnect_count})...")
        await asyncio.sleep(delay)
    
    async def _cleanup_connection(self):
        """Cleanup current connection"""
        try:
            # Disconnect provider
            if self.provider:
                await self.provider.disconnect()
                self.provider = None
            
            self.w3 = None
        
        except Exception as e:
            print(f"[WS] Cleanup connection error: {e}")
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            # Unsubscribe from all pools
            for pool_address in list(self.event_filters.keys()):
                await self._unsubscribe_pool_async(pool_address)
            
            # Cleanup connection
            await self._cleanup_connection()
        
        except Exception as e:
            print(f"[WS] Cleanup error: {e}")
