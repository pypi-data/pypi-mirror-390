# USDT/ASTER Pool Guide

## Pool Information

**Token Pair**: USDT / ASTER  
**Network**: BSC (Binance Smart Chain)  
**DEX**: PancakeSwap V3

### Available Pools

| Fee Tier | Fee | Pool Address |
|----------|-----|--------------|
| 0.05% | 500 | `0x7E58f160B5B77b8B24Cd9900C09A3E730215aC47` |
| **0.25%** ⭐ | **2500** | **`0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1`** |
| 1% | 10000 | `0x3817fF61B34c5Ff5dc89709B2Db1f194299e3BA9` |

**Recommended**: Use 0.25% pool (most liquid typically)

### Token Addresses

- **USDT**: `0x55d398326f99059fF775485246999027B3197955`
- **ASTER**: `0x000Ae314E2A2172a039B26378814C252734f556A`

## Quick Start

### 1. Basic Quote

```python
from web3 import Web3
from quoter import QuoterV3
from state import StateFetcher
import config

# Setup
w3 = Web3(Web3.HTTPProvider(config.BSC_RPC_URL))
quoter = QuoterV3(w3, StateFetcher(w3))

# Pool address (0.25% fee)
POOL = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"

# Fetch pool state once
pool_state = quoter.add_pool(POOL)

# Check token order
print(f"Token0: {pool_state.token0}")
print(f"Token1: {pool_state.token1}")

# Quote: 1000 USDT -> ASTER
amount_out = quoter.quote_exact_input_single(
    pool_address=POOL,
    zero_for_one=True,  # Depends on token order!
    amount_in=1000 * 10**18,  # 1000 USDT
)

print(f"Amount out: {amount_out / 10**18} ASTER")
```

### 2. Determine Swap Direction

**IMPORTANT**: Bạn phải check token order trước!

```python
USDT = "0x55d398326f99059fF775485246999027B3197955"

pool_state = quoter.add_pool(POOL)

# Check which token is token0
if pool_state.token0.lower() == USDT.lower():
    # USDT là token0
    # USDT -> ASTER: zero_for_one = True
    # ASTER -> USDT: zero_for_one = False
    print("USDT is token0")
else:
    # USDT là token1
    # USDT -> ASTER: zero_for_one = False
    # ASTER -> USDT: zero_for_one = True
    print("USDT is token1")
```

### 3. High-Frequency Trading Setup

```python
# Setup với background updates
state_fetcher = StateFetcher(w3)
quoter = QuoterV3(w3, state_fetcher)

# Add pool
POOL = "0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1"
quoter.add_pool(POOL)

# Start auto-update (mỗi 500ms)
state_fetcher.start_background_update(
    pool_addresses=[POOL],
    interval=0.5,
)

# Trading loop - quote nhanh vì state updated liên tục
try:
    while True:
        # Quote (< 1ms)
        amount_out = quoter.quote_exact_input_single(
            pool_address=POOL,
            zero_for_one=True,
            amount_in=1000 * 10**18,
        )
        
        # Your trading logic here...
        print(f"Current quote: {amount_out / 10**18} ASTER")
        
        time.sleep(0.1)  # Check every 100ms
        
except KeyboardInterrupt:
    state_fetcher.stop_background_update()
```

## Running Examples

### Example 1: Basic Usage
```bash
python example_usdt_aster.py
```

### Example 2: Find All Pools
```bash
python get_pool_address.py
```

## Token Decimals

Both tokens use **18 decimals**:
- USDT: 18 decimals
- ASTER: 18 decimals

### Converting Amounts

```python
# Human readable -> Contract format
amount_human = 1000  # 1000 USDT
amount_contract = amount_human * 10**18

# Contract format -> Human readable
amount_contract = 1000000000000000000000  # From quote
amount_human = amount_contract / 10**18
```

## Checking Pool on BscScan

1. Go to: https://bscscan.com/address/0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1
2. View contract details
3. Check Read Contract functions:
   - `slot0()` - Current price and tick
   - `liquidity()` - Current liquidity
   - `token0()` / `token1()` - Token addresses

## Tips & Best Practices

### 1. Always Check Token Order
Token order trong pool có thể là USDT/ASTER hoặc ASTER/USDT. Luôn check trước khi quote.

### 2. Update Frequency
- High frequency: 100-500ms
- Normal: 500-1000ms
- Low frequency: 1-5s

### 3. Error Handling
```python
try:
    amount_out = quoter.quote_exact_input_single(...)
except Exception as e:
    print(f"Quote failed: {e}")
    # Handle error (maybe state is stale, re-fetch)
```

### 4. Price Calculation
```python
# USDT per ASTER
price = (amount_in_usdt / 10**18) / (amount_out_aster / 10**18)
print(f"1 ASTER = {price:.6f} USDT")

# ASTER per USDT
price_inverse = 1 / price
print(f"1 USDT = {price_inverse:.6f} ASTER")
```

## Performance Expectations

- **Initial fetch**: ~100-200ms
- **Quote (cached)**: < 1ms
- **State update**: ~50-100ms
- **Throughput**: 1000+ quotes/sec

## Troubleshooting

### Pool State Outdated
```python
# Manually update pool state
quoter.update_pool(POOL)
```

### Connection Issues
```python
# Try different RPC
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed1.binance.org/"))
```

### Quote Returns 0
- Check liquidity: `pool_state.liquidity`
- Check amount: Không quá lớn
- Check direction: `zero_for_one` đúng chưa?

## Resources

- **PancakeSwap Info**: https://pancakeswap.finance/info/v3/pairs/0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1
- **BscScan**: https://bscscan.com/address/0xaeaD6bd31dd66Eb3A6216aAF271D0E661585b0b1
- **Pool Analytics**: Check DEX analytics sites for volume, TVL, etc.

---

**Created**: 2025-11-07  
**Pool**: USDT/ASTER 0.25%  
**Network**: BSC

