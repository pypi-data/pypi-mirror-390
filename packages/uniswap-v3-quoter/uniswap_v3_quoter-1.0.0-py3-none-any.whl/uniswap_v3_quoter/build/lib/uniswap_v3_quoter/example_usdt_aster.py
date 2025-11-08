"""
Example: Quote USDT/ASTER swap on PancakeSwap V3
Pool: 0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1 (0.25% fee)
"""

from web3 import Web3
from quoter import QuoterV3
from state import StateFetcher
import config
import time

# Token addresses
USDT = "0x55d398326f99059fF775485246999027B3197955"
ASTER = "0x000Ae314E2A2172a039B26378814C252734f556A"

# Pool address (0.25% fee tier)
POOL_ADDRESS = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"


def main():
    """Quote USDT/ASTER swap"""
    
    print("="*60)
    print("USDT/ASTER Swap Quote Example")
    print("="*60)
    
    # Connect to BSC
    print("\n1. Connecting to BSC...")
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC")
        return
    
    print(f"✅ Connected (block: {w3.eth.block_number})")
    
    # Initialize quoter
    print("\n2. Initializing quoter...")
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    print("✅ Quoter initialized")
    
    # Add pool
    print(f"\n3. Fetching pool state...")
    print(f"   Pool: {POOL_ADDRESS}")
    
    try:
        pool_state = quoter.add_pool(POOL_ADDRESS)
        
        print(f"✅ Pool state fetched:")
        print(f"   Token0: {pool_state.token0}")
        print(f"   Token1: {pool_state.token1}")
        print(f"   Fee: {pool_state.fee / 10000}%")
        print(f"   Tick Spacing: {pool_state.tick_spacing}")
        print(f"   Current Tick: {pool_state.tick}")
        print(f"   Liquidity: {pool_state.liquidity}")
        
        # Determine token order
        if pool_state.token0.lower() == USDT.lower():
            token0_name = "USDT"
            token1_name = "ASTER"
        else:
            token0_name = "ASTER"
            token1_name = "USDT"
        
        print(f"\n   Token0 = {token0_name}")
        print(f"   Token1 = {token1_name}")
        
    except Exception as e:
        print(f"❌ Error fetching pool: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Example 1: Quote USDT -> ASTER
    print("\n" + "="*60)
    print("Example 1: Quote 1000 USDT -> ASTER")
    print("="*60)
    
    # USDT has 18 decimals
    amount_in_usdt = 1000 * 10**18
    
    # Determine direction: USDT -> ASTER
    if pool_state.token0.lower() == USDT.lower():
        # USDT is token0, so we swap token0 -> token1 (zero_for_one = True)
        zero_for_one = True
        print(f"\nSwap direction: token0 (USDT) -> token1 (ASTER)")
    else:
        # USDT is token1, so we swap token1 -> token0 (zero_for_one = False)
        zero_for_one = False
        print(f"\nSwap direction: token1 (USDT) -> token0 (ASTER)")
    
    print(f"Amount in: {amount_in_usdt / 10**18} USDT")
    
    try:
        start = time.time()
        amount_out = quoter.quote_exact_input_single(
            pool_address=POOL_ADDRESS,
            zero_for_one=zero_for_one,
            amount_in=amount_in_usdt,
        )
        elapsed = (time.time() - start) * 1000
        
        print(f"\n✅ Quote successful!")
        print(f"   Amount out: {amount_out / 10**18} ASTER")
        print(f"   Quote time: {elapsed:.2f}ms")
        
        # Calculate price
        price = (amount_in_usdt / 10**18) / (amount_out / 10**18)
        print(f"   Price: 1 ASTER = {price:.6f} USDT")
        
    except Exception as e:
        print(f"❌ Quote failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Example 2: Quote ASTER -> USDT
    print("\n" + "="*60)
    print("Example 2: Quote 10000 ASTER -> USDT")
    print("="*60)
    
    amount_in_aster = 10000 * 10**18
    
    # Determine direction: ASTER -> USDT (opposite of above)
    zero_for_one = not zero_for_one
    
    if zero_for_one:
        print(f"\nSwap direction: token0 (ASTER) -> token1 (USDT)")
    else:
        print(f"\nSwap direction: token1 (ASTER) -> token0 (USDT)")
    
    print(f"Amount in: {amount_in_aster / 10**18} ASTER")
    
    try:
        start = time.time()
        amount_out = quoter.quote_exact_input_single(
            pool_address=POOL_ADDRESS,
            zero_for_one=zero_for_one,
            amount_in=amount_in_aster,
        )
        elapsed = (time.time() - start) * 1000
        
        print(f"\n✅ Quote successful!")
        print(f"   Amount out: {amount_out / 10**18} USDT")
        print(f"   Quote time: {elapsed:.2f}ms")
        
        # Calculate price
        price = (amount_out / 10**18) / (amount_in_aster / 10**18)
        print(f"   Price: 1 ASTER = {price:.6f} USDT")
        
    except Exception as e:
        print(f"❌ Quote failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Benchmark
    print("\n" + "="*60)
    print("Benchmark: 100 quotes")
    print("="*60)
    
    num_quotes = 100
    print(f"\nRunning {num_quotes} quotes...")
    
    start = time.time()
    for i in range(num_quotes):
        quoter.quote_exact_input_single(
            pool_address=POOL_ADDRESS,
            zero_for_one=True,
            amount_in=amount_in_usdt,
        )
    elapsed = time.time() - start
    
    print(f"✅ Complete!")
    print(f"   Total time: {elapsed:.2f}s")
    print(f"   Average: {(elapsed / num_quotes) * 1000:.2f}ms per quote")
    print(f"   Throughput: {num_quotes / elapsed:.0f} quotes/sec")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

