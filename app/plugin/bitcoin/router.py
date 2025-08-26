from app.plugin.bitcoin.blockchain import BlockchainPriceSpot
from app.plugin.bitcoin.coingecko import CoinGeckoPriceSpot
from app.plugin.bitcoin.kraken import KrakenPriceSpot
from app.plugin.bitcoin.menpool import MempoolPriceSpot
from app.plugin.bitcoin.ninjas import NinjasPriceSpot
from app.plugin.bitcoin.coinstats import CoinStatsPriceSpot
from .coinbase_price_spot import CoinbasePriceSpot
from .binance_price_spot import BinancePriceSpot


def register_processor(bitcoin_processors: list, processor_class: type):
    try:
        if not any(isinstance(proc, processor_class) for proc in bitcoin_processors):
            processor = processor_class()
            bitcoin_processors.append(processor)
            print(f"✅ {processor.get_source_name()} processor registered successfully.")
        else:
            print(f"⚠️  {processor_class.__name__} processor is already registered.")
    except Exception as e:
        print(f"❌ Failed to register {processor_class.__name__} processor: {e}")


def register_all_processors(bitcoin_processors: list):
    """
    Register all available Bitcoin processors.
    
    Args:
        bitcoin_processors (list): List to register processors into
    """
    register_processor(bitcoin_processors, BinancePriceSpot)
    register_processor(bitcoin_processors, CoinbasePriceSpot)
    register_processor(bitcoin_processors, KrakenPriceSpot)
    register_processor(bitcoin_processors, CoinGeckoPriceSpot)
    register_processor(bitcoin_processors, BlockchainPriceSpot)
    register_processor(bitcoin_processors, MempoolPriceSpot)
    register_processor(bitcoin_processors, CoinStatsPriceSpot)
    register_processor(bitcoin_processors, NinjasPriceSpot) 
    