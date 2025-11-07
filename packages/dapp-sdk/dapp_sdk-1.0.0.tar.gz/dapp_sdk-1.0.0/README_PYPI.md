# DAPP SDK - Python

Official Python client for the DAPP AI Cost Platform. Measure, verify, and standardize AI computational costs across providers using Decentralized Compute Units (DCU).

## Features

- **Token Counting**: Accurate token counting using official provider tokenizers
- **DCU Calculation**: Convert provider-specific costs to standardized DCU
- **Markup Validation**: Real-time tolerance breach detection
- **Efficiency Ratios**: Calculate and compare provider efficiency
- **Carbon Footprint**: Track sustainability metrics
- **ROI Computation**: Comprehensive cost-benefit analysis

## Installation

```bash
pip install dapp-sdk
```

## Quick Start

```python
from dapp_sdk import DAPPClient
import os

# Initialize client
client = DAPPClient(
    base_url=os.getenv("DAPP_API_URL", "https://your-production-domain.com"),
    api_key="your-api-key"
)

# Count tokens with official tokenizers
result = client.count_tokens(
    text="Hello, world!",
    model="gpt-4"
)
print(f"Tokens: {result['tokenCount']}")

# Calculate DCU cost
dcu_result = client.calculate_dcu(
    input_tokens=100,
    output_tokens=50,
    model="gpt-4",
    provider="openai"
)
print(f"DCU Cost: {dcu_result['dcuCost']}")
```

## Environment Variables

Set `DAPP_API_URL` to your DAPP platform URL:

```bash
export DAPP_API_URL=https://your-domain.com
```

## Documentation

Full documentation available at [docs.dapp-platform.com](https://docs.dapp-platform.com)

## Support

- Email: support@dapp-platform.com
- Issues: https://github.com/dapp-platform/dapp-sdk/issues

## License

MIT License - see LICENSE file for details
