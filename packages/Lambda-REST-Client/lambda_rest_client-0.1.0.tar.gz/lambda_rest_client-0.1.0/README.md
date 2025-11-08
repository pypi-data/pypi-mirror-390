# Lambda-REST-Client

A simple Python client for calling AWS Lambda REST endpoints asynchronously using `aiohttp`.  

## Installation

You can install the package from PyPI:

```bash
pip install Lambda-REST-Client
````

## Usage

```python
from lambda_rest_client import LambdaClient

client = LambdaClient(endpoint="https://your-lambda-endpoint.com")

# Example async call
import asyncio

async def main():
    response = await client.call(payload={"key": "value"})
    print(response)

asyncio.run(main())
```

## Requirements

* Python 3.8+
* aiohappyeyeballs==2.6.1
* aiohttp==3.13.2
* aiosignal==1.4.0
* attrs==25.4.0
* frozenlist==1.8.0
* idna==3.11
* multidict==6.7.0
* propcache==0.4.1
* yarl==1.22.0

## License

3-Clause BSD NON-AI License
See [LICENSE](LICENSE) for details.

