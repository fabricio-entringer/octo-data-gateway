from app.plugin.bitcoin.block_cypher_balance import BlockCypherBalance
from app.plugin.bitcoin.blockchain_balance import BlockchainBalance
from app.plugin.bitcoin.blockchain_price import BlockchainPriceSpot
from app.plugin.bitcoin.blockchair_balance import BlockChairBalance
from app.plugin.bitcoin.blockstream_balance import BlockstreamBalance
from app.plugin.bitcoin.coingecko_price import CoinGeckoPriceSpot
from app.plugin.bitcoin.kraken_price import KrakenPriceSpot
from app.plugin.bitcoin.menpool_price import MempoolPriceSpot
from app.plugin.bitcoin.coinstats_price import CoinStatsPriceSpot
from .coinbase_price import CoinbasePriceSpot
from .binance_price import BinancePriceSpot
from app.plugin.plugins_register import register_processor


bitcoin_price_processors = []
__price_resource_list = [BinancePriceSpot, CoinbasePriceSpot, KrakenPriceSpot, CoinGeckoPriceSpot,
                   BlockchainPriceSpot, MempoolPriceSpot, CoinStatsPriceSpot]


bitcoin_balance_processors = []
__balance_resource_list = [BlockChairBalance, BlockCypherBalance, BlockstreamBalance, BlockchainBalance]


# Register plugins when module is imported
def _register_plugins():
    """Register all available Bitcoin plugins."""

    print("\033[94m💰 [Bitcoin] Starting registration of Bitcoin plugins...\033[0m")
    for processor in __price_resource_list:
        register_processor(bitcoin_price_processors, processor)

    for processor in __balance_resource_list:
        register_processor(bitcoin_balance_processors, processor)

    print("\033[94m💰 [Bitcoin] All Bitcoin plugins have been registered!\033[0m")


# Auto-register plugins
_register_plugins()    
    