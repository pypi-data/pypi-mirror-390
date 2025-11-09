import pytest

from simplepushoverclient.pushover import PushoverClient, PUSHOVER_API_URL
from simplepushoverclient.exceptions import PushoverExceptionResponse


def test_client_send_ok(requests_mock) -> None:
    # Arrange
    requests_mock.post(PUSHOVER_API_URL, status_code=200, json={"status": 1, "request": "abc-123"})

    client = PushoverClient(token="mytoken")

    # Act
    status = client.send("myuser", "Hello World")

    # Assert
    assert status == 200


def test_client_send_invalid_token(requests_mock) -> None:
    # Arrange
    requests_mock.post(
        PUSHOVER_API_URL,
        status_code=400,
        json={
            "token": "invalid",
            "errors": "application token is invalid, see https://pushover.net/api",
            "status": 0,
            "request": "abc-123",
        },
    )

    client = PushoverClient(token="mytoken")

    # Act
    with pytest.raises(PushoverExceptionResponse) as exc:
        client.send("myuser", "Hello World!")

        # Assert
        assert exc.status_code == 400
        assert exc.message == "application token is invalid, see https://pushover.net/api"
        assert str(exc) == "400: application token is invalid, see https://pushover.net/api"


def test_client_send_invalid_user(requests_mock) -> None:
    # Arrange
    requests_mock.post(
        PUSHOVER_API_URL,
        status_code=400,
        json={
            "token": "invalid",
            "errors": "user identifier is not a valid user, group, or subscribed user key, see https://pushover.net/api#identifiers",
            "status": 0,
            "request": "abc-123",
        },
    )

    client = PushoverClient(token="mytoken")

    # Act
    with pytest.raises(PushoverExceptionResponse) as exc:
        client.send("myuser", "Hello World!")

        # Assert
        assert exc.status_code == 400
        assert (
            exc.message
            == "user identifier is not a valid user, group, or subscribed user key, see https://pushover.net/api#identifiers"
        )
        assert (
            str(exc)
            == "400: user identifier is not a valid user, group, or subscribed user key, see https://pushover.net/api#identifiers"
        )
