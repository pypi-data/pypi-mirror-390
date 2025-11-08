"""
Example: WebSocket Realtime Updates
Demonstrates using WebSocket subscriptions for low-latency pool state updates
"""

import time
from web3 import Web3

from quoter import QuoterV3
from state import StateFetcher, WebSocketSubscriber, SwapEventData
import config


def main():
    """Example: Real-time quotes with WebSocket updates"""
    
    print("=" * 70)
    print("WebSocket Realtime Updates Example")
    print("=" * 70)
    print()
    
    # Pool to monitor
    POOL_ADDRESS = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"  # USDT/ASTER 0.25%
    
    print(f"Pool: {POOL_ADDRESS}")
    print()
    
    # Step 1: Connect to BSC
    print("1. Connecting to BSC...")
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC")
        return
    
    print(f"✓ Connected (block: {w3.eth.block_number})")
    print()
    
    # Step 2: Initialize quoter and fetch initial state
    print("2. Initializing quoter...")
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    
    print("✓ Quoter initialized")
    print()
    
    print("3. Fetching initial pool state...")
    pool_state = quoter.add_pool(POOL_ADDRESS)
    
    print(f"✓ Pool state:")
    print(f"   Token0: {pool_state.token0}")
    print(f"   Token1: {pool_state.token1}")
    print(f"   Fee: {pool_state.fee / 10000}%")
    print(f"   Current tick: {pool_state.tick}")
    print(f"   Liquidity: {pool_state.liquidity}")
    print()
    
    # Step 4: Setup WebSocket subscriber
    print("4. Setting up WebSocket subscriber...")
    
    # Track updates
    update_count = 0
    last_update_time = time.time()
    
    def on_swap_event(swap_data: SwapEventData):
        """Callback when Swap event received"""
        nonlocal update_count, last_update_time
        
        update_count += 1
        current_time = time.time()
        latency = (current_time - swap_data.timestamp) * 1000  # ms
        
        # Update pool state automatically via StateFetcher
        state_fetcher.update_from_swap_event(swap_data)
        
        print(f"\n[Update #{update_count}] Swap detected!")
        print(f"  Block: {swap_data.block_number}")
        print(f"  TX: {swap_data.transaction_hash[:10]}...")
        print(f"  New tick: {swap_data.tick}")
        print(f"  New liquidity: {swap_data.liquidity}")
        print(f"  Amount0: {swap_data.amount0 / 10**18:.6f}")
        print(f"  Amount1: {swap_data.amount1 / 10**18:.6f}")
        print(f"  Latency: {latency:.2f}ms")
        
        # Try a quote
        try:
            amount_in = 1000 * 10**18  # 1000 tokens
            quote_start = time.time()
            amount_out = quoter.quote_exact_input_single(
                pool_address=POOL_ADDRESS,
                zero_for_one=False,  # token1 -> token0
                amount_in=amount_in,
            )
            quote_time = (time.time() - quote_start) * 1000
            
            print(f"  Quote: {amount_in / 10**18:.2f} → {amount_out / 10**18:.6f} (took {quote_time:.2f}ms)")
        except Exception as e:
            print(f"  Quote failed: {e}")
        
        last_update_time = current_time
    
    # Check if WSS URL is configured
    if not config.BSC_WSS_URL:
        print("❌ BSC_WSS_URL not configured in config.py")
        print("   Please set a WebSocket endpoint to use this feature")
        return
    
    try:
        ws_subscriber = WebSocketSubscriber(
            wss_url=config.BSC_WSS_URL,
            callback=on_swap_event,
            reconnect_max_retries=config.WS_RECONNECT_MAX_RETRIES,
            reconnect_delay=config.WS_RECONNECT_DELAY,
            reconnect_max_delay=config.WS_RECONNECT_MAX_DELAY,
        )
        
        # Subscribe to pool
        ws_subscriber.subscribe_pool(POOL_ADDRESS)
        
        # Start subscriber
        ws_subscriber.start()
        
        print("✓ WebSocket subscriber started")
        print()
        print("=" * 70)
        print("Listening for Swap events... (Press Ctrl+C to stop)")
        print("=" * 70)
        print()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
                
                # Show status every 30 seconds
                if time.time() - last_update_time > 30:
                    print(f"[Status] Waiting for swaps... ({update_count} updates so far)")
                    last_update_time = time.time()
        
        except KeyboardInterrupt:
            print("\n\nStopping...")
        
        finally:
            # Cleanup
            ws_subscriber.stop()
            print("\n✓ WebSocket subscriber stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def compare_polling_vs_websocket():
    """Compare performance: Polling vs WebSocket"""
    
    print("\n" + "=" * 70)
    print("Performance Comparison: Polling vs WebSocket")
    print("=" * 70)
    print()
    
    POOL_ADDRESS = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"
    
    # Connect
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    state_fetcher = StateFetcher(w3)
    quoter = QuoterV3(w3, state_fetcher)
    
    # Fetch initial state
    quoter.add_pool(POOL_ADDRESS)
    
    print("Method 1: Multicall Polling")
    print("-" * 70)
    
    # Benchmark polling
    polling_times = []
    for i in range(10):
        start = time.time()
        state_fetcher.update_pool_state(POOL_ADDRESS)
        elapsed = (time.time() - start) * 1000
        polling_times.append(elapsed)
        print(f"  Update {i+1}: {elapsed:.2f}ms")
    
    avg_polling = sum(polling_times) / len(polling_times)
    print(f"\n  Average: {avg_polling:.2f}ms")
    print()
    
    print("Method 2: WebSocket Events")
    print("-" * 70)
    print("  Updates triggered only when actual Swap occurs")
    print("  Typical latency: < 10ms (from event to callback)")
    print("  No unnecessary RPC calls")
    print()
    
    print("Comparison:")
    print("-" * 70)
    print(f"  Polling:   {avg_polling:.2f}ms per update (updates constantly)")
    print(f"  WebSocket: < 10ms latency (updates only on swaps)")
    print(f"  Improvement: ~{avg_polling / 10:.1f}x faster for realtime updates")
    print()
    print("Additional Benefits:")
    print("  - Reduced RPC usage (no polling)")
    print("  - Lower latency (push vs pull)")
    print("  - More efficient (event-driven)")
    print()


if __name__ == "__main__":
    main()
    
    # Uncomment to run comparison
    # compare_polling_vs_websocket()

