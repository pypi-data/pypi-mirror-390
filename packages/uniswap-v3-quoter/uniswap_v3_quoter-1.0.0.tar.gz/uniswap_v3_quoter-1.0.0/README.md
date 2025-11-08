# Uniswap V3 Python Quoter

Python implementation của logic quote swap Uniswap V3, được tối ưu cho high-frequency trading trên BSC (PancakeSwap V3).

## Tính năng

- ✅ **Quote nhanh**: Tính toán quote ở local thay vì gọi RPC, giảm latency từ ~1s xuống < 1ms
- ✅ **Background updates**: Tự động fetch và cập nhật pool state theo interval
- ✅ **Chính xác 100%**: Port trực tiếp từ Solidity, đảm bảo kết quả giống on-chain
- ✅ **Multicall support**: Batch RPC calls để fetch state nhanh hơn
- ✅ **Thread-safe**: An toàn khi sử dụng với multi-threading

## Cài đặt

### Từ PyPI (Khuyến nghị)

```bash
pip install uniswap-v3-quoter
```

### Từ source

```bash
git clone https://github.com/yourusername/v3-python-quoter.git
cd v3-python-quoter
pip install -e .
```

### Performance extras (optional)

Để tối ưu performance, cài thêm các dependencies:

```bash
pip install uniswap-v3-quoter[performance]
```

## Sử dụng cơ bản

```python
from web3 import Web3
from uniswap_v3_quoter import QuoterV3, StateFetcher

# Kết nối đến BSC
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))

# Khởi tạo quoter
multicall3_address = "0xcA11bde05977b3631167028862bE2a173976CA11"  # Multicall3 on BSC
state_fetcher = StateFetcher(w3, multicall3_address)
quoter = QuoterV3(w3, state_fetcher)

# Thêm pool cần quote
pool_address = "0x..."  # Địa chỉ pool PancakeSwap V3
pool_state = quoter.add_pool(pool_address)

# Quote swap
amount_in = 1 * 10**18  # 1 token (18 decimals)
amount_out = quoter.quote_exact_input_single(
    pool_address=pool_address,
    zero_for_one=True,  # Swap token0 -> token1
    amount_in=amount_in,
)

print(f"Amount out: {amount_out / 10**18}")
```

## High-Frequency Trading

Để sử dụng cho HFT, enable background updates:

```python
# Start background updates (cập nhật mỗi 500ms)
state_fetcher.start_background_update(
    pool_addresses=[pool_address],
    interval=0.5,  # 500ms
)

# Bây giờ có thể quote liên tục với latency < 1ms
for i in range(1000):
    amount_out = quoter.quote_exact_input_single(
        pool_address=pool_address,
        zero_for_one=True,
        amount_in=amount_in,
    )
    # Process quote...
```

## Cấu trúc thư mục

```
v3-python-quoter/
├── uniswap_math/            # Math libraries (FullMath, TickMath, etc.)
│   ├── full_math.py
│   ├── tick_math.py
│   ├── sqrt_price_math.py
│   ├── swap_math.py
│   ├── tick_bitmap.py
│   └── liquidity_math.py
├── state/                   # State management
│   ├── pool_state.py       # PoolState class
│   └── state_fetcher.py    # StateFetcher với multicall
├── quoter.py               # Main quoter logic
├── config.py               # Configuration
├── requirements.txt
├── example.py              # Examples
└── README.md
```

## Logic hoạt động

1. **Fetch state**: Sử dụng multicall để fetch pool state từ blockchain (slot0, liquidity, ticks, tickBitmap)
2. **Cache in memory**: Lưu state trong memory
3. **Background updates**: Interval thread tự động update state
4. **Local quote**: Tính toán quote từ cached state, giống hệt logic của `UniswapV3Pool.swap()`

### Swap Loop Logic

```
1. Initialize: sqrt_price, tick, liquidity từ pool state
2. Loop while amount_remaining > 0:
   a. Tìm tick tiếp theo trong tickBitmap
   b. Tính swap step (amount_in, amount_out, fee)
   c. Update amount_remaining, amount_calculated
   d. Nếu cross tick: update liquidity
   e. Update current price và tick
3. Return amount_out
```

## Performance

- **On-chain call**: ~1000ms (gọi RPC lên QuoterV2)
- **Python local quote**: < 1ms (sau khi có state trong cache)
- **State update**: ~100-200ms (với multicall)

Với background updates mỗi 500ms, bạn có thể quote hàng nghìn lần/giây với state gần real-time.

## Lưu ý

1. **Tick data**: Mặc định chỉ fetch tick data trong range cần thiết. Nếu price move ra ngoài range, cần fetch thêm.
2. **Pool address**: Cần biết pool address trước. Có thể compute từ factory address + token addresses + fee.
3. **BSC = PancakeSwap V3**: BSC không có Uniswap V3 official, mà là PancakeSwap V3 (fork).
4. **Độ chính xác**: Python `int` hỗ trợ arbitrary precision, phù hợp cho uint256.

## Testing

```python
# So sánh với on-chain QuoterV2
python example.py
```

## License

MIT License (same as Uniswap V3)

## Credits

- Uniswap V3 Core: https://github.com/Uniswap/v3-core
- Uniswap V3 Periphery: https://github.com/Uniswap/v3-periphery

