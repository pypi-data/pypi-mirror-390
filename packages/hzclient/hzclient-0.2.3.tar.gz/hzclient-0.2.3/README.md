# hzclient

Simple Python client for Hero Zero game API.

## Usage

```python
from hzclient import GameState, Client, Config

state = GameState()
client = Client(
  config=Config(
    server_id="pl1",
    email="testuser@example.com",
    password="testpass"
  ),
  state=state
)

client.login()

print(state.character.name) # Name of your character

client.call("someAPIMethod", {"param1": "value1"}) # Call any API method, handles session automatically
```

## Features

- No documentation available.
  - Read the `hzclient/state.py` file to see available attributes in `GameState`.
  - Read the `hzclient/client.py` file to see available methods in `Client`.