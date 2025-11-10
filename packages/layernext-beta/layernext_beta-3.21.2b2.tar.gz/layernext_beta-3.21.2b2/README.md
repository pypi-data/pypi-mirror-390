# layernext-python-sdk

LayerNext python API client

Sync (upload/download) with LayerNext stacks via APIs from your code

## Installation

`$ pip install layernext`

## Usage

```python
import layernext

api_key = 'xxxxxxxxxx'
secret = 'xxxxxxxxxxx'
url = 'https://api.xxxx.layernext.ai'

client = layernext.LayerNextClient(api_key, secret, url)

```

## Building Python SDK
1. Set the correct version in `__init__.py`
2. Build the package
    - Make sure the Python virtual environment is set
    - Clean the dist folder : `rm -r dist`
    - Build the package : `python setup.py sdist bdist_wheel`
3. Upload the package
    - Use twine to upload the package : `twine upload dist/*`
    - Use the correct key for beta

