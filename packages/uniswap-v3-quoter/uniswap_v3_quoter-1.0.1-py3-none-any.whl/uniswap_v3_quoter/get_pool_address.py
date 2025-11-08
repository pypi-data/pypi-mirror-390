"""
Helper script to get Uniswap V3 / PancakeSwap V3 pool address
"""

from web3 import Web3
import config

# PancakeSwap V3 Factory ABI (getPool function)
FACTORY_ABI = [
    {
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "fee", "type": "uint24"}
        ],
        "name": "getPool",
        "outputs": [{"name": "pool", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]


def get_pool_address(
    w3: Web3,
    factory_address: str,
    token_a: str,
    token_b: str,
    fee: int,
) -> str:
    """
    Get pool address from factory contract
    
    Args:
        w3: Web3 instance
        factory_address: Factory contract address
        token_a: First token address
        token_b: Second token address
        fee: Fee tier (500, 2500, 10000, etc.)
    
    Returns:
        Pool address (or zero address if pool doesn't exist)
    """
    # Convert to checksum addresses
    factory_address = Web3.to_checksum_address(factory_address)
    token_a = Web3.to_checksum_address(token_a)
    token_b = Web3.to_checksum_address(token_b)
    
    # Create factory contract instance
    factory = w3.eth.contract(address=factory_address, abi=FACTORY_ABI)
    
    # Query pool address
    pool_address = factory.functions.getPool(token_a, token_b, fee).call()
    
    return pool_address


def main():
    """Example: Get USDT/ASTER pool address"""
    
    # Connect to BSC
    print("Connecting to BSC...")
    w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to BSC")
        return
    
    print(f"✅ Connected to BSC (block: {w3.eth.block_number})\n")
    
    # Token addresses
    USDT = "0x55d398326f99059fF775485246999027B3197955"
    ASTER = "0x000Ae314E2A2172a039B26378814C252734f556A"
    
    # Fee tiers to check
    fee_tiers = {
        "0.05%": 500,
        "0.25%": 2500,
        "1%": 10000,
    }
    
    print("Searching for USDT/ASTER pools on PancakeSwap V3...\n")
    print(f"Token A (USDT): {USDT}")
    print(f"Token B (ASTER): {ASTER}\n")
    
    # Check each fee tier
    for fee_name, fee_value in fee_tiers.items():
        print(f"Checking {fee_name} (fee={fee_value})...")
        
        try:
            pool_address = get_pool_address(
                w3,
                config.PANCAKESWAP_V3_FACTORY,
                USDT,
                ASTER,
                fee_value,
            )
            
            # Check if pool exists (not zero address)
            if pool_address != "0x0000000000000000000000000000000000000000":
                print(f"  ✅ Pool found: {pool_address}\n")
                
                # Get more info about the pool
                try:
                    from quoter import QuoterV3
                    from state import StateFetcher
                    
                    state_fetcher = StateFetcher(w3)
                    quoter = QuoterV3(w3, state_fetcher)
                    
                    print(f"  Fetching pool state...")
                    pool_state = quoter.add_pool(pool_address)
                    
                    print(f"  Token0: {pool_state.token0}")
                    print(f"  Token1: {pool_state.token1}")
                    print(f"  Fee: {pool_state.fee / 10000}%")
                    print(f"  Current tick: {pool_state.tick}")
                    print(f"  Liquidity: {pool_state.liquidity}")
                    print()
                    
                except Exception as e:
                    print(f"  (Could not fetch pool details: {e})\n")
            else:
                print(f"  ❌ Pool not found\n")
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    print("\n" + "="*60)
    print("To use this pool with the quoter:")
    print("="*60)
    print("""
from quoter import QuoterV3
from state import StateFetcher
from web3 import Web3
import config

w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
quoter = QuoterV3(w3, StateFetcher(w3))

# Add pool
pool_address = "0x..."  # Use the address found above
quoter.add_pool(pool_address)

# Quote swap
amount_out = quoter.quote_exact_input_single(
    pool_address=pool_address,
    zero_for_one=True,  # True if swapping token0 -> token1
    amount_in=1_000_000_000_000_000_000,  # 1 token
)

print(f"Amount out: {amount_out}")
""")


if __name__ == "__main__":
    main()

