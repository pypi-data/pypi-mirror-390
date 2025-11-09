# SimplePushoverClient
A simple client for the Pushover notification service.

## Usage

```
from SimplePushoverClient.pushover import PushoverClient

if __name__ == "__main__":
    client = PushoverClient(token="my_token")
    client.send(user="my_user", message="my_msg", device="device", title="title")
```