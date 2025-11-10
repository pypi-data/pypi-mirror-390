# SkyBlue Bridge

Python client for interacting with the SkyBlue MT5 bridge microservice.

## Installation

```bash
pip install skyblue-bridge
```

## Usage

```python
from skyblue_bridge import MTClient

client = MTClient(api_key="your-api-key")
print(client.get_server_status())
```
