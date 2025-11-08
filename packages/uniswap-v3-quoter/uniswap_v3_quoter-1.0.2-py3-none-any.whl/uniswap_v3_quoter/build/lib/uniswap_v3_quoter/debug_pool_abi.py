"""
Debug script to check PancakeSwap V3 pool ABI
"""

from web3 import Web3
import config
from eth_abi import decode

# Connect
w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
pool = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"

print("Debugging PancakeSwap V3 Pool ABI")
print("="*60)
print(f"Pool: {pool}")
print(f"Connected: {w3.is_connected()}")
print()

# Test slot0()
print("Testing slot0()...")
selector = w3.keccak(text='slot0()')[:4]
print(f"Selector: {selector.hex()}")

result = w3.eth.call({'to': pool, 'data': selector})
print(f"Raw result length: {len(result)} bytes")
print(f"Raw result (hex): {result.hex()}")
print()

# Try different decode formats
print("Trying different decode formats...")
print()

# Standard Uniswap V3 slot0
try:
    print("1. Standard Uniswap V3 format:")
    print("   (uint160, int24, uint16, uint16, uint16, uint8, bool)")
    data = decode(
        ["uint160", "int24", "uint16", "uint16", "uint16", "uint8", "bool"],
        result,
    )
    print(f"   ✅ Success: {data}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Try with uint256 for observationCardinalityNext
try:
    print("2. With uint256 for observationCardinalityNext:")
    print("   (uint160, int24, uint16, uint16, uint256, uint8, bool)")
    data = decode(
        ["uint160", "int24", "uint16", "uint16", "uint256", "uint8", "bool"],
        result,
    )
    print(f"   ✅ Success: {data}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Try without strict validation
try:
    print("3. Trying manual parsing...")
    # Parse manually
    sqrtPriceX96 = int.from_bytes(result[0:32], 'big')
    tick_raw = int.from_bytes(result[32:64], 'big')
    # int24 conversion
    if tick_raw >= 2**23:
        tick = tick_raw - 2**24
    else:
        tick = tick_raw
    
    observationIndex = int.from_bytes(result[64:96], 'big')
    observationCardinality = int.from_bytes(result[96:128], 'big')
    observationCardinalityNext = int.from_bytes(result[128:160], 'big')
    feeProtocol = int.from_bytes(result[160:192], 'big')
    unlocked = int.from_bytes(result[192:224], 'big')
    
    print(f"   sqrtPriceX96: {sqrtPriceX96}")
    print(f"   tick: {tick}")
    print(f"   observationIndex: {observationIndex}")
    print(f"   observationCardinality: {observationCardinality}")
    print(f"   observationCardinalityNext: {observationCardinalityNext}")
    print(f"   feeProtocol: {feeProtocol}")
    print(f"   unlocked: {unlocked}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Check other functions
print("="*60)
print("Testing other functions...")
print()

# liquidity()
print("Testing liquidity()...")
selector = w3.keccak(text='liquidity()')[:4]
result = w3.eth.call({'to': pool, 'data': selector})
print(f"Raw: {result.hex()}")
try:
    liquidity = decode(["uint128"], result)[0]
    print(f"✅ Liquidity: {liquidity}")
except Exception as e:
    print(f"❌ Failed: {e}")
print()

# fee()
print("Testing fee()...")
selector = w3.keccak(text='fee()')[:4]
result = w3.eth.call({'to': pool, 'data': selector})
print(f"Raw: {result.hex()}")
try:
    fee = decode(["uint24"], result)[0]
    print(f"✅ Fee: {fee}")
except Exception as e:
    print(f"❌ Failed: {e}")
print()

# tickSpacing()
print("Testing tickSpacing()...")
selector = w3.keccak(text='tickSpacing()')[:4]
result = w3.eth.call({'to': pool, 'data': selector})
print(f"Raw: {result.hex()}")
try:
    tickSpacing = decode(["int24"], result)[0]
    print(f"✅ TickSpacing: {tickSpacing}")
except Exception as e:
    print(f"❌ Failed: {e}")
print()

print("="*60)
print("Recommendation:")
print("Check the actual contract ABI on BscScan:")
print(f"https://bscscan.com/address/{pool}#code")

