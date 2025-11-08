"""
Test and validate Quoter against on-chain QuoterV2
"""

import time
from web3 import Web3
from quoter import QuoterV3
from state import StateFetcher
import config


# QuoterV2 ABI (simplified - just quoteExactInputSingle)
QUOTER_V2_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"name": "amountOut", "type": "uint256"},
            {"name": "sqrtPriceX96After", "type": "uint160"},
            {"name": "initializedTicksCrossed", "type": "uint32"},
            {"name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


def test_against_on_chain(
    w3: Web3,
    quoter_v2_address: str,
    pool_address: str,
    amount_in: int,
    zero_for_one: bool,
):
    """
    Test Python quoter against on-chain QuoterV2
    
    Args:
        w3: Web3 instance
        quoter_v2_address: Address of on-chain QuoterV2 contract
        pool_address: Pool to test
        amount_in: Amount to quote
        zero_for_one: Swap direction
    """
    print("=== Testing Python Quoter vs On-Chain QuoterV2 ===\n")
    
    # Initialize Python quoter
    print("1. Initializing Python quoter...")
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    
    # Fetch pool state
    print(f"2. Fetching pool state for {pool_address}...")
    start = time.time()
    pool_state = quoter.add_pool(pool_address)
    fetch_time = (time.time() - start) * 1000
    print(f"   Pool state fetched in {fetch_time:.2f}ms")
    print(f"   Token0: {pool_state.token0}")
    print(f"   Token1: {pool_state.token1}")
    print(f"   Fee: {pool_state.fee / 10000}%")
    print(f"   Current tick: {pool_state.tick}")
    print(f"   Liquidity: {pool_state.liquidity}")
    
    # Quote with Python
    print(f"\n3. Quoting with Python quoter...")
    print(f"   Amount in: {amount_in / 10**18} tokens")
    print(f"   Direction: {'token0 -> token1' if zero_for_one else 'token1 -> token0'}")
    
    start = time.time()
    python_amount_out = quoter.quote_exact_input_single(
        pool_address=pool_address,
        zero_for_one=zero_for_one,
        amount_in=amount_in,
    )
    python_time = (time.time() - start) * 1000
    
    print(f"   Python result: {python_amount_out / 10**18} tokens")
    print(f"   Python time: {python_time:.2f}ms")
    
    # Quote with on-chain QuoterV2
    print(f"\n4. Quoting with on-chain QuoterV2...")
    quoter_v2 = w3.eth.contract(
        address=Web3.to_checksum_address(quoter_v2_address),
        abi=QUOTER_V2_ABI,
    )
    
    token_in = pool_state.token0 if zero_for_one else pool_state.token1
    token_out = pool_state.token1 if zero_for_one else pool_state.token0
    
    start = time.time()
    try:
        result = quoter_v2.functions.quoteExactInputSingle(
            (token_in, token_out, amount_in, pool_state.fee, 0)
        ).call()
        on_chain_amount_out = result[0]
        on_chain_time = (time.time() - start) * 1000
        
        print(f"   On-chain result: {on_chain_amount_out / 10**18} tokens")
        print(f"   On-chain time: {on_chain_time:.2f}ms")
        
        # Compare results
        print(f"\n5. Comparison:")
        print(f"   Python: {python_amount_out}")
        print(f"   On-chain: {on_chain_amount_out}")
        
        difference = abs(python_amount_out - on_chain_amount_out)
        diff_percentage = (difference / on_chain_amount_out) * 100 if on_chain_amount_out > 0 else 0
        
        print(f"   Difference: {difference} ({diff_percentage:.6f}%)")
        
        if difference == 0:
            print("   ✅ EXACT MATCH!")
        elif diff_percentage < 0.0001:
            print("   ✅ Match within rounding error")
        else:
            print("   ⚠️  Significant difference detected")
        
        print(f"\n6. Performance:")
        print(f"   Python: {python_time:.2f}ms")
        print(f"   On-chain: {on_chain_time:.2f}ms")
        print(f"   Speedup: {on_chain_time / python_time:.1f}x faster")
        
    except Exception as e:
        print(f"   Error calling on-chain quoter: {e}")
        print(f"   (This might be expected if QuoterV2 uses try-catch mechanism)")


def benchmark_python_quoter(
    w3: Web3,
    pool_address: str,
    amount_in: int,
    zero_for_one: bool,
    num_iterations: int = 1000,
):
    """
    Benchmark Python quoter performance
    """
    print("\n=== Benchmarking Python Quoter ===\n")
    
    # Initialize
    state_fetcher = StateFetcher(w3, config.MULTICALL3_ADDRESS)
    quoter = QuoterV3(w3, state_fetcher)
    
    # Fetch pool state
    print("Fetching pool state...")
    quoter.add_pool(pool_address)
    
    # Warm up
    print("Warming up...")
    for _ in range(10):
        quoter.quote_exact_input_single(
            pool_address=pool_address,
            zero_for_one=zero_for_one,
            amount_in=amount_in,
        )
    
    # Benchmark
    print(f"Running {num_iterations} quotes...")
    start = time.time()
    
    for _ in range(num_iterations):
        quoter.quote_exact_input_single(
            pool_address=pool_address,
            zero_for_one=zero_for_one,
            amount_in=amount_in,
        )
    
    elapsed = time.time() - start
    avg_time = (elapsed / num_iterations) * 1000
    
    print(f"\nResults:")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Average time per quote: {avg_time:.3f}ms")
    print(f"  Quotes per second: {num_iterations / elapsed:.0f}")


def test_math_libraries():
    """
    Test math libraries with known values
    """
    print("\n=== Testing Math Libraries ===\n")
    
    from uniswap_math import (
        get_sqrt_ratio_at_tick,
        get_tick_at_sqrt_ratio,
        MIN_TICK,
        MAX_TICK,
        MIN_SQRT_RATIO,
        MAX_SQRT_RATIO,
    )
    
    # Test TickMath
    print("Testing TickMath...")
    
    # Test MIN_TICK
    min_sqrt_ratio = get_sqrt_ratio_at_tick(MIN_TICK)
    assert min_sqrt_ratio == MIN_SQRT_RATIO, f"MIN_SQRT_RATIO mismatch: {min_sqrt_ratio} != {MIN_SQRT_RATIO}"
    print(f"  ✅ MIN_TICK -> MIN_SQRT_RATIO: {min_sqrt_ratio}")
    
    # Test MAX_TICK
    max_sqrt_ratio = get_sqrt_ratio_at_tick(MAX_TICK)
    assert max_sqrt_ratio == MAX_SQRT_RATIO, f"MAX_SQRT_RATIO mismatch: {max_sqrt_ratio} != {MAX_SQRT_RATIO}"
    print(f"  ✅ MAX_TICK -> MAX_SQRT_RATIO: {max_sqrt_ratio}")
    
    # Test tick 0 (price = 1)
    tick_0_sqrt_ratio = get_sqrt_ratio_at_tick(0)
    expected = 79228162514264337593543950336  # 2^96
    assert tick_0_sqrt_ratio == expected, f"Tick 0 mismatch: {tick_0_sqrt_ratio} != {expected}"
    print(f"  ✅ Tick 0 -> sqrt(1) * 2^96: {tick_0_sqrt_ratio}")
    
    # Test roundtrip (exclude MIN_TICK and MAX_TICK as their sqrt ratios are boundary values)
    test_ticks = [-887271, -100000, -1000, 0, 1000, 100000, 887271]
    for tick in test_ticks:
        sqrt_ratio = get_sqrt_ratio_at_tick(tick)
        recovered_tick = get_tick_at_sqrt_ratio(sqrt_ratio)
        assert recovered_tick == tick, f"Roundtrip failed for tick {tick}: got {recovered_tick}"
    print(f"  ✅ Roundtrip test passed for {len(test_ticks)} ticks")
    
    print("\nAll math tests passed! ✅")


def main():
    """
    Main test function
    """
    # Test math libraries first
    test_math_libraries()
    
    # Connect to BSC
    print("\n=== Connecting to BSC ===\n")
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC")
        return
    
    print(f"✅ Connected to BSC (block: {w3.eth.block_number})")
    
    # Get pool address from user
    print("\n=== Pool Testing ===\n")
    pool_address = input("Enter PancakeSwap V3 pool address to test (or press Enter to skip): ").strip()
    
    if not pool_address:
        print("Skipping pool tests")
        return
    
    # Get QuoterV2 address
    quoter_v2_address = input("Enter QuoterV2 address (or press Enter to skip on-chain comparison): ").strip()
    
    # Test parameters
    amount_in = 1 * 10**18  # 1 token
    zero_for_one = True
    
    # Run benchmark
    benchmark_python_quoter(w3, pool_address, amount_in, zero_for_one, num_iterations=100)
    
    # Compare with on-chain if available
    if quoter_v2_address:
        test_against_on_chain(w3, quoter_v2_address, pool_address, amount_in, zero_for_one)
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    main()

