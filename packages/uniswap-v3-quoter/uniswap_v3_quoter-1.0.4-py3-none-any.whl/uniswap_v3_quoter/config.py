"""
Configuration for Uniswap V3 Python Quoter
"""

# BSC Configuration
BSC_RPC_URL = "https://bsc-dataseed.binance.org/"
BSC_RPC_URLS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed3.binance.org/",
    "https://bsc-dataseed4.binance.org/",
]

# WebSocket Configuration
# For production, use a reliable WSS provider like Alchemy, Infura, or QuickNode
BSC_WSS_URL = "wss://cosmopolitan-sparkling-arrow.bsc.quiknode.pro/833002b5d68ae8582e9d5bb74ac381a52ec5add5/"
# Alternative WSS providers (commented out, uncomment to use):
# BSC_WSS_URL = "wss://bsc-mainnet.nodereal.io/ws/v1/YOUR_API_KEY"
# BSC_WSS_URL = "wss://speedy-nodes-nyc.moralis.io/YOUR_API_KEY/bsc/mainnet/ws"

# Multicall3 address (same on most chains)
MULTICALL3_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

# Uniswap V3 Factory address on BSC (PancakeSwap V3)
# Note: BSC uses PancakeSwap V3 which is a fork of Uniswap V3
PANCAKESWAP_V3_FACTORY = "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"

# Common token addresses on BSC
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
USDT = "0x55d398326f99059fF775485246999027B3197955"
USDC = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
CAKE = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
ETH = "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
BTCB = "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9C"

# Common fee tiers
FEE_LOW = 500  # 0.05%
FEE_MEDIUM = 2500  # 0.25%
FEE_HIGH = 10000  # 1%

# Default update interval for background state fetching (in seconds)
DEFAULT_UPDATE_INTERVAL = 0.5  # 500ms for high frequency trading

# Maximum number of ticks to pre-fetch around current price
DEFAULT_TICK_RANGE = 1000  # Fetch ±1000 ticks around current tick

# WebSocket Settings
USE_WEBSOCKET = True  # Enable WebSocket subscription for realtime updates
WS_RECONNECT_MAX_RETRIES = 5  # Maximum reconnection attempts
WS_RECONNECT_DELAY = 1.0  # Initial delay between reconnections (seconds)
WS_RECONNECT_MAX_DELAY = 30.0  # Maximum delay between reconnections (seconds)
WS_PING_INTERVAL = 20.0  # Keepalive ping interval (seconds)
WS_PING_TIMEOUT = 10.0  # Ping timeout (seconds)

