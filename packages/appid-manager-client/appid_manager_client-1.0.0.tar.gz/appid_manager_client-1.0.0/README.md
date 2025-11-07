# AppID Manager Client

A Python SDK for managing AppID resources with support for concurrent access and product isolation.

## Features

- 🚀 **Concurrent Access**: Support for high-concurrency AppID acquisition
- 🔒 **Product Isolation**: Separate AppID pools for different business products
- ⏰ **Hourly Boundaries**: Strict adherence to hourly AppID usage limits
- 🔄 **Polling Support**: Automatic retry and wait mechanisms
- 🛡️ **Error Handling**: Robust error handling and timeout management
- 📊 **Status Monitoring**: Real-time AppID status and statistics

## Installation

```bash
pip install appid-manager-client
```

## Quick Start

```python
from appid_manager_client import AppIdClient

# Create client
client = AppIdClient("http://localhost:5000")

# Initialize product AppIDs
client.init_product("stt_billing", {
    "appid1": "vid1",
    "appid2": "vid2"
})

# Acquire AppID
appid, vid, start_time, product_name = client.acquire_appid("stt_billing")

# Use AppID for your business logic
print(f"Using AppID: {appid}, VID: {vid}")

# Release AppID when done
client.release_appid(appid, "stt_billing")
```

## API Reference

### AppIdClient

#### `__init__(base_url, timeout)`
Initialize the AppID client.

- `base_url` (str): Server URL (default: "http://101.64.234.17:8888")
- `timeout` (int): Request timeout in seconds (default: 5)

#### `acquire_appid(product_name, max_retries, retry_interval)`
Acquire an available AppID.

- `product_name` (str): Product name (required)
- `max_retries` (int): Maximum retry attempts (default: 60)
- `retry_interval` (int): Retry interval in seconds (default: 60)

Returns: `(appid, vid, start_time, product_name)`

#### `release_appid(appid, product_name)`
Release an AppID.

- `appid` (str): AppID to release
- `product_name` (str): Product name (required)

Returns: `bool` - Success status

#### `init_product(product_name, appids)`
Initialize or reset product AppID configuration.

- `product_name` (str): Product name
- `appids` (dict): AppID configuration {appid: vid}

Returns: `bool` - Success status

#### `get_status(product_name)`
Get AppID status statistics.

- `product_name` (str, optional): Filter by product name

Returns: `dict` - Status information

#### `health_check()`
Check service health.

Returns: `bool` - Health status

## Configuration

The client supports configuration through environment variables:

- `APPID_MANAGER_URL`: Server URL
- `APPID_MANAGER_TIMEOUT`: Request timeout

## Error Handling

The client handles various error scenarios:

- **Connection errors**: Automatic retry with exponential backoff
- **Timeout errors**: Configurable timeout and retry logic
- **Service unavailable**: Graceful degradation and error reporting
- **AppID exhaustion**: Polling and waiting for availability

## Examples

### Basic Usage

```python
from appid_manager_client import AppIdClient

client = AppIdClient()

# Health check
if not client.health_check():
    print("Service unavailable")
    exit(1)

# Initialize product
client.init_product("my_product", {
    "appid_001": "vid_001",
    "appid_002": "vid_002"
})

# Acquire and use AppID
try:
    appid, vid, start_time, product = client.acquire_appid("my_product")
    print(f"Acquired: {appid} (VID: {vid})")
    
    # Your business logic here
    
finally:
    client.release_appid(appid, "my_product")
```

### Concurrent Usage

```python
import threading
from appid_manager_client import AppIdClient

def worker(client, product_name, worker_id):
    try:
        appid, vid, start_time, product = client.acquire_appid(product_name)
        print(f"Worker {worker_id}: Got {appid}")
        
        # Simulate work
        time.sleep(10)
        
        client.release_appid(appid, product_name)
        print(f"Worker {worker_id}: Released {appid}")
        
    except Exception as e:
        print(f"Worker {worker_id}: Error - {e}")

# Create multiple workers
client = AppIdClient()
threads = []

for i in range(5):
    thread = threading.Thread(target=worker, args=(client, "stt_billing", i))
    threads.append(thread)
    thread.start()

# Wait for all workers
for thread in threads:
    thread.join()
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/your-username/appid-manager-client.git
cd appid-manager-client
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black appid_manager_client/
flake8 appid_manager_client/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
