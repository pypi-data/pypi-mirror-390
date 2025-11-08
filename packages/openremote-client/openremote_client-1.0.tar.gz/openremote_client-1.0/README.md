# OpenRemote Client
A Python client to use the OpenRemote Manager REST API.

---
[![PyPI version shields.io](https://img.shields.io/pypi/v/openremote_client.svg)](https://pypi.python.org/pypi/openremote_client/)
[![PyPI - Downloads](https://img.shields.io/pypi/dd/openremote_client)](https://pypi.python.org/pypi/openremote_client/)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/Spider-Frog/openremote_client/blob/main/LICENSE.txt)


## Getting started
1. Install package
```shell
pip install openremote_client
```

2. Then import the package into your project.

```python
from openremote_client import OpenRemoteClient
```

3. Now initialize the OpenRemote client with some config.
```python
or_client = OpenRemoteClient(
    openremote_host='<openremote_manager_url>',
    client_id='<openremote_client_id>',
    client_secret='<openremote_client_secret>'
)
```

Finally you can use the client to call the OpenRemote Manager REST API
```python
# Get Asset by id
asset = await or_client.asset.get_by_id('<asset-id>')

# Query mulitple assets
asset = await or_client.asset.query({
    "limit": 5
})
```

The client handles authentication automatically.


## Development guide
### Installation
Prerequisites 
  - Python 3.10+ installed

1. Clone repository
```shell
git clone https://github.com/Spider-Frog/openremote_client.git
```

2. Install packages
```shell
pip install -r requirements.txt
```


### Deploy
Read the documentation on [PyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)