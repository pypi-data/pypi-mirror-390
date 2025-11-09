import pytest
import json
from simplepushoverclient.models import SendMessageModel


@pytest.mark.parametrize(
    "input_data,expected_data",
    [
        (
            {"token": "abc", "user": "123", "message": "hello world!"},
            {"token": "abc", "user": "123", "message": "hello world!"},
        ),
        (
            {"token": "abc", "user": "123", "message": "hello world!", "title": "title"},
            {"token": "abc", "user": "123", "title": "title", "message": "hello world!"},
        ),
    ],
)
def test_send_msg_dump(input_data: dict, expected_data: dict) -> None:
    """tests the SendMessageModel.dump method"""
    # Arrange
    model = SendMessageModel(**input_data)

    # Act
    dump = model.dump()

    # Assert
    assert json.dumps(expected_data) == json.dumps(dump)
