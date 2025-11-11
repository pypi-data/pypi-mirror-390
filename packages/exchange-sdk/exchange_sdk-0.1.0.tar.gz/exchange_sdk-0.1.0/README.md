# Python SDK

Minimal asyncio-based client that speaks the exchange binary TCP order protocol and listens for UDP market-data packets. Use this as the reference implementation when onboarding student teams.

## Quick Installation

### Windows
```bash
# Double-click install_sdk.bat
# OR run in PowerShell:
pip install -e .
```

### Linux/Mac
```bash
# Run the installer:
./install_sdk.sh

# OR manually:
pip install -e .
```

## Verify Installation

```bash
python -c "from exchange_sdk import ExchangeClient; print('SDK installed!')"
```

## Usage Example

```python
from exchange_sdk import ExchangeClient
from exchange_sdk.client import GatewayConfig, MarketDataConfig

# Connect to exchange
client = ExchangeClient(
    team_token="your-team-SECRET",
    gateway=GatewayConfig(host="159.65.173.202", port=9001),
    market_data=MarketDataConfig(host="159.65.173.202", port=5001)
)

# Connect and trade
await client.connect()
client.send_new(
    client_id=1,
    symbol_id=1,      # XYZ
    side=0,           # BUY
    price_ticks=10000,  # $100.00
    quantity=10
)
await client.close()
```

## What You Need

- Python 3.11 or higher
- The SDK installed (`pip install -e .`)
- Your team token (provided by organizers)
- Exchange host/port (provided by organizers)

## For Competition Participants

See [INSTALL_SDK.md](INSTALL_SDK.md) for detailed installation instructions and troubleshooting.

