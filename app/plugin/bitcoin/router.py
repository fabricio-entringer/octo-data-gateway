from .binance_price_spot import BinancePriceSpot


def register_bitcoin_processor(bitcoin_processors: list):
    """
    Registers the BinancePriceSpot processor to the bitcoin_processors list.
    This allows the application to use Binance as a source for Bitcoin price data.
    
    Args:
        bitcoin_processors (list): List to register processors into
    """
    try:
        if not any(isinstance(proc, BinancePriceSpot) for proc in bitcoin_processors):
            processor = BinancePriceSpot()
            bitcoin_processors.append(processor)
            print("✅ BinancePriceSpot processor registered successfully.")
        else:
            print("⚠️  BinancePriceSpot processor is already registered.")
    except Exception as e:
        print(f"❌ Failed to register BinancePriceSpot processor: {e}")


def register_all_processors(bitcoin_processors: list):
    """
    Register all available Bitcoin processors.
    
    Args:
        bitcoin_processors (list): List to register processors into
    """
    register_bitcoin_processor(bitcoin_processors)
    # Add more processors here in the future
    # register_coinbase_processor(bitcoin_processors)
    # register_kraken_processor(bitcoin_processors)