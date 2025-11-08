"""
Example usage of Uniswap V3 Python Quoter
"""

import time
from web3 import Web3

from quoter import QuoterV3
from state import StateFetcher
import config


def main():
    """Example: Quote a swap on PancakeSwap V3 (BSC)"""
    
    # Setup Web3 connection
    print("Connecting to BSC...")
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("Failed to connect to BSC")
        return
    
    print(f"Connected! Latest block: {w3.eth.block_number}")
    
    # Initialize quoter
    print("\nInitializing quoter...")
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    
    # Example: WBNB/BUSD pool on PancakeSwap V3
    # You need to provide the actual pool address
    # This is just an example structure
    
    # For demonstration, let's show how to use the quoter:
    print("\n=== Example Usage ===\n")
    
    print("Step 1: Add a pool to the quoter")
    print("   pool_address = '0x...'  # Your pool address")
    print("   pool_state = quoter.add_pool(pool_address)")
    print()
    
    print("Step 2: Quote a swap")
    print("   amount_in = 1 * 10**18  # 1 token with 18 decimals")
    print("   zero_for_one = True  # Swapping token0 for token1")
    print("   amount_out = quoter.quote_exact_input_single(")
    print("       pool_address=pool_address,")
    print("       zero_for_one=zero_for_one,")
    print("       amount_in=amount_in,")
    print("   )")
    print("   print(f'Amount out: {amount_out}')")
    print()
    
    print("Step 3: Start background updates (optional, for high-frequency trading)")
    print("   state_fetcher.start_background_update(")
    print("       pool_addresses=[pool_address],")
    print("       interval=0.5,  # Update every 500ms")
    print("   )")
    print()
    
    print("Step 4: Quote repeatedly (fast because state is cached)")
    print("   for i in range(100):")
    print("       amount_out = quoter.quote_exact_input_single(...)")
    print("       # Process quote...")
    print()
    
    # Example with actual pool (if available)
    print("\n=== Live Example (if pool address provided) ===\n")
    
    # You can replace this with an actual pool address
    example_pool = input("Enter a PancakeSwap V3 pool address (or press Enter to skip): ").strip()
    
    if example_pool:
        try:
            print(f"\nFetching pool state for {example_pool}...")
            pool_state = quoter.add_pool(example_pool)
            
            print(f"Pool State:")
            print(f"  Token0: {pool_state.token0}")
            print(f"  Token1: {pool_state.token1}")
            print(f"  Fee: {pool_state.fee / 10000}%")
            print(f"  Current tick: {pool_state.tick}")
            print(f"  Current price (sqrt): {pool_state.sqrt_price_x96}")
            print(f"  Liquidity: {pool_state.liquidity}")
            
            # Try a quote
            amount_in = 1 * 10**18  # 1 token (assuming 18 decimals)
            print(f"\nQuoting swap: {amount_in / 10**18} token0 -> token1")
            
            start_time = time.time()
            amount_out = quoter.quote_exact_input_single(
                pool_address=example_pool,
                zero_for_one=True,
                amount_in=amount_in,
            )
            elapsed = (time.time() - start_time) * 1000
            
            print(f"Amount out: {amount_out / 10**18} token1")
            print(f"Quote time: {elapsed:.2f}ms")
            
            # Benchmark multiple quotes
            print("\nBenchmarking 100 quotes...")
            start_time = time.time()
            for i in range(100):
                quoter.quote_exact_input_single(
                    pool_address=example_pool,
                    zero_for_one=True,
                    amount_in=amount_in,
                )
            elapsed = (time.time() - start_time) * 1000
            print(f"Average quote time: {elapsed / 100:.2f}ms")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Skipped live example")
    
    print("\n=== Complete ===")


def example_with_background_updates():
    """
    Example: Using background updates for high-frequency trading
    """
    print("=== Example: Background Updates ===\n")
    
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("Failed to connect to BSC")
        return
    
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    
    # Add pools
    pool_addresses = [
        # Add your pool addresses here
        # "0x...",
        '0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1'
    ]
    
    if not pool_addresses:
        print("No pool addresses provided. Add pool addresses to this example.")
        return
    
    # Fetch initial state
    for pool_address in pool_addresses:
        quoter.add_pool(pool_address)
    
    # Start background updates
    state_fetcher.start_background_update(
        pool_addresses=pool_addresses,
        interval=config.DEFAULT_UPDATE_INTERVAL,
    )
    
    print("Background updates started. Pool states will be updated every 500ms.")
    print("You can now call quote functions repeatedly with minimal latency.")
    
    try:
        # Simulate high-frequency quoting
        for i in range(10):
            pool_state = quoter.get_pool(pool_addresses[0])
            print(f"\nIteration {i + 1}:")
            print(f"  Current tick: {pool_state.tick}")
            print(f"  Last update: {time.time() - pool_state.last_update_timestamp:.2f}s ago")
            
            # Quote
            amount_out = quoter.quote_exact_input_single(
                pool_address=pool_addresses[0],
                zero_for_one=True,
                amount_in=1 * 10**18,
            )
            print(f"  Quote: {amount_out / 10**18} tokens")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        # Stop background updates
        state_fetcher.stop_background_update()
        print("Background updates stopped.")


if __name__ == "__main__":
    # main()
    
    # Uncomment to run the background updates example
    example_with_background_updates()

