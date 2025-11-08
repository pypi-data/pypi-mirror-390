# Quick Start Guide

## Installation

```bash
cd v3-python-quoter
pip install -r requirements.txt
```

## Minimal Example (5 bước)

```python
from web3 import Web3
from quoter import QuoterV3
from state import StateFetcher

# 1. Connect to BSC
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))

# 2. Initialize quoter
quoter = QuoterV3(w3, StateFetcher(w3))

# 3. Add pool (thay bằng pool address thật)
pool = quoter.add_pool("0xYourPoolAddress")

# 4. Quote swap
amount_out = quoter.quote_exact_input_single(
    pool_address=pool.address,
    zero_for_one=True,        # token0 -> token1
    amount_in=1_000_000_000_000_000_000,  # 1 token (18 decimals)
)

# 5. Use result
print(f"You will receive: {amount_out / 10**18} tokens")
```

## High-Frequency Trading Bot

```python
from web3 import Web3
from quoter import QuoterV3
from state import StateFetcher
import time

# Setup
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
state_fetcher = StateFetcher(w3)
quoter = QuoterV3(w3, state_fetcher)

# Add pools you want to monitor
POOL_1 = "0x..."
POOL_2 = "0x..."

quoter.add_pool(POOL_1)
quoter.add_pool(POOL_2)

# Start auto-update (update state every 500ms in background)
state_fetcher.start_background_update(
    pool_addresses=[POOL_1, POOL_2],
    interval=0.5,
)

# Trading loop - quote nhanh vì state đã có sẵn
try:
    while True:
        # Quote pool 1
        amount_out_1 = quoter.quote_exact_input_single(
            pool_address=POOL_1,
            zero_for_one=True,
            amount_in=1 * 10**18,
        )
        
        # Quote pool 2
        amount_out_2 = quoter.quote_exact_input_single(
            pool_address=POOL_2,
            zero_for_one=True,
            amount_in=1 * 10**18,
        )
        
        # Trading logic
        if amount_out_1 > amount_out_2 * 1.01:  # 1% arbitrage
            print(f"Arbitrage opportunity! {amount_out_1} vs {amount_out_2}")
            # Execute trade...
        
        time.sleep(0.1)  # Check mỗi 100ms
        
except KeyboardInterrupt:
    state_fetcher.stop_background_update()
```

## Finding Pool Address

### Option 1: From Factory
```python
# Compute pool address from token pair + fee
# (Chưa implement - cần thêm CREATE2 logic)
```

### Option 2: From Block Explorer
1. Vào BscScan
2. Tìm token pair bạn muốn trade
3. Tìm PancakeSwap V3 pool contract
4. Copy address

### Option 3: From PancakeSwap
1. Vào https://pancakeswap.finance/
2. Chọn token pair
3. Check "Pool Info" để lấy address

## Configuration

Edit `config.py`:
```python
# Change RPC if needed
BSC_RPC_URL = "https://your-private-rpc.com"

# Adjust update interval
DEFAULT_UPDATE_INTERVAL = 0.3  # 300ms instead of 500ms
```

## Testing

```bash
# Run basic tests
python test_quoter.py

# With your pool
python test_quoter.py
# Enter your pool address when prompted
```

## Common Issues

### 1. "Pool state not found"
**Cause**: Chưa gọi `quoter.add_pool()`  
**Fix**: Gọi `quoter.add_pool(pool_address)` trước khi quote

### 2. "Connection refused"
**Cause**: RPC endpoint down  
**Fix**: Thử RPC khác trong `config.BSC_RPC_URLS`

### 3. Quote result khác nhiều so với expected
**Cause**: State đã cũ (nhiều swaps xảy ra sau khi fetch)  
**Fix**: 
- Giảm update interval
- Fetch state mới trước khi quote quan trọng

### 4. "Tick not initialized"
**Cause**: Price di chuyển ra ngoài range ticks đã fetch  
**Fix**: Fetch wider tick range khi add pool

## Performance Tips

1. **Batch pool additions**: Add nhiều pools cùng lúc thay vì từng pool
2. **Tune update interval**: 500ms là default, có thể giảm xuống 100ms
3. **Pre-fetch tick range**: Fetch wider range nếu volatility cao
4. **Use connection pooling**: Tái sử dụng Web3 connection
5. **Consider websocket**: Thay HTTP RPC bằng WebSocket nếu có

## Next Steps

1. Integrate vào trading bot của bạn
2. Backtest với historical data
3. Deploy lên production với monitoring
4. Scale ra nhiều pools/pairs

## Support

- Đọc `README.md` cho full documentation
- Xem `example.py` cho more examples
- Check `docs/uniswap-v3-python-quoter-summary.md` cho technical details

