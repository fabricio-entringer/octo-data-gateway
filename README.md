# 🌐 External Data Gateway

<div align="center">

**A robust, extensible gateway for external data access with built-in authentication, rate limiting, and plugin architecture.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 📋 Overview

External Data Gateway is a centralized service that provides secure, standardized access to external data sources. It features a plugin architecture for easy extensibility, API key-based authentication with granular scopes, and comprehensive error handling with structured responses.

### ✨ Key Features

- 🔐 **Secure Authentication** - API key-based auth with granular scope permissions
- 🔌 **Plugin Architecture** - Extensible design for adding new data sources
- 📊 **Structured Responses** - Consistent API responses with metadata
- ⚡ **High Performance** - Built with FastAPI for optimal performance
- 🛡️ **Error Handling** - Comprehensive exception handling with detailed error codes
- 📈 **Bitcoin Data** - Real-time Bitcoin price data from multiple sources
- 🗃️ **Lightweight Database** - TinyDB for simple, file-based data storage

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fabricio-entringer/external-data-gateway.git
   cd external-data-gateway
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Run the application**
   ```bash
   make run
   ```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

## 🔑 Authentication

The gateway uses API key authentication with scope-based permissions. A default master user is automatically created on first run:

```bash
# Look for output similar to:
Created default user: Default Master User (ID: a565f715-c450-4410-806c-3c3b63fc14c4)
API Key: 7a3e9242-7828-46c3-aae5-dd83d3acdb72
```

### Available Scopes

- `MASTER` - Full access to all endpoints
- `BITCOIN` - Access to Bitcoin-related endpoints
- `EXCHANGE_RATES` - Access to exchange rate endpoints (future)

### Making Authenticated Requests

Include the API key in the `X-API-KEY` header:

```bash
curl -H "X-API-KEY: your-api-key-here" \
     http://localhost:8000/api/v1/bitcoin/price?currency=USD
```

## 📚 API Reference

### Bitcoin Endpoints

#### Get Bitcoin Price
```http
GET /api/v1/bitcoin/price
```

**Parameters:**
- `currency` (query, optional): Target currency (default: USD)
- `source` (query, optional): Data source preference
- `accept_cache` (query, optional): Accept cached responses (default: true)

**Headers:**
- `X-API-KEY` (required): Your API key

**Response:**
```json
{
  "data": {
    "bitcoin_price": {
      "price": 45000.50,
      "currency": "USD",
      "source": "Binance"
    }
  },
  "metadata": {
    "user_id": "a565f715-c450-4410-806c-3c3b63fc14c4",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp_request_received": "2023-01-01T12:00:00Z",
    "timestamp_response_sent": "2023-01-01T12:00:01Z",
    "api_version": "v1",
    "is_successful": true,
    "processing_time_ms": 245.8,
    "app_version": "0.0.1"
  }
}
```

## 🏗️ Architecture

### Project Structure

```
external-data-gateway/
├── app/                          # Main application package
│   ├── api/                      # API layer
│   │   ├── bitcoin/              # Bitcoin-specific endpoints
│   │   │   ├── controller.py     # Route handlers
│   │   │   ├── service.py        # Business logic
│   │   │   ├── schema.py         # Pydantic models
│   │   │   └── bitcoin_exception.py  # Custom exceptions
│   │   └── routes.py             # API router configuration
│   ├── core/                     # Core functionality
│   │   ├── models.py             # Shared data models
│   │   ├── security.py           # Authentication & authorization
│   │   └── custom_exception.py   # Base exception classes
│   ├── database/                 # Data layer
│   │   ├── models.py             # Database models
│   │   └── user_database.py      # User management
│   ├── plugin/                   # Plugin system
│   │   └── bitcoin/              # Bitcoin plugins
│   │       ├── router.py         # Plugin registration
│   │       └── binance_price_spot.py  # Binance implementation
│   └── main.py                   # FastAPI application
├── data/                         # Database files
├── Makefile                      # Development commands
├── pyproject.toml               # Project configuration
└── run.py                       # Application entry point
```

### Plugin System

The gateway uses a plugin architecture for extensibility. To add a new Bitcoin data source:

1. **Create a new processor** implementing `BitcoinProcessor`:
   ```python
   class YourExchangeProcessor(BitcoinProcessor):
       def get_bitcoin_price_external(self, currency: str) -> Dict:
           # Implementation here
           pass
       
       def get_source_name(self) -> str:
           return "YourExchange"
   ```

2. **Register the processor** in `plugin/bitcoin/router.py`:
   ```python
   def register_your_exchange_processor(bitcoin_processors: list):
       processor = YourExchangeProcessor()
       bitcoin_processors.append(processor)
   ```

## 🛠️ Development

### Available Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make test          # Run tests
make type-check    # Run type checking
make clean         # Clean build artifacts
make build         # Build package
make run           # Run the application
```

### Adding New Features

1. **New API endpoints**: Add to `app/api/`
2. **New data sources**: Create plugins in `app/plugin/`
3. **New authentication scopes**: Add to `app/database/models.py`
4. **Custom exceptions**: Extend base classes in `app/core/`

### Error Handling

The gateway uses structured error responses with specific error codes:

```python
# Example error response
{
  "data": null,
  "metadata": {
    "error_info": {
      "error_code": "EAG_BTC_002",
      "error_message": "Bitcoin price data is not available.",
      "error_details": "Timeout occurred while fetching data",
      "category": "SERVICE",
      "retryable": true
    }
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
make test
```

For type checking:

```bash
make type-check
```

## 📝 Configuration

### Environment Variables

The application can be configured through environment variables (future enhancement):

- `EDG_HOST`: Server host (default: 0.0.0.0)
- `EDG_PORT`: Server port (default: 8000)
- `EDG_LOG_LEVEL`: Logging level (default: info)

### Database

The gateway uses TinyDB for lightweight, file-based data storage. Database files are stored in the `data/` directory.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add new exchange rate endpoint
fix: resolve Bitcoin price fetching issue
docs: update API documentation
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [TinyDB](https://tinydb.readthedocs.io/) for lightweight database functionality
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

---

<div align="center">
Made with ❤️ by <a href="mailto:fabricio@entringer.dev">Fabricio Entringer</a>
</div>
