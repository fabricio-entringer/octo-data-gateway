from app.plugin.bitcoin.blockchain import BlockchainPriceSpot
from app.plugin.bitcoin.coingecko import CoinGeckoPriceSpot
from app.plugin.bitcoin.kraken import KrakenPriceSpot
from app.plugin.bitcoin.menpool import MempoolPriceSpot
from app.plugin.bitcoin.coinstats import CoinStatsPriceSpot
from .coinbase_price_spot import CoinbasePriceSpot
from .binance_price_spot import BinancePriceSpot
from app.plugin.plugins_register import register_processor


bitcoin_processors = []
__resource_list = [BinancePriceSpot, CoinbasePriceSpot, KrakenPriceSpot, CoinGeckoPriceSpot,
                   BlockchainPriceSpot, MempoolPriceSpot, CoinStatsPriceSpot]


# Register plugins when module is imported
def _register_plugins():
    """Register all available Bitcoin plugins."""
    for processor in __resource_list:
        register_processor(bitcoin_processors, processor)


# Auto-register plugins
_register_plugins()    
    