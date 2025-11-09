from typing import Optional
from pydantic import BaseModel, Field


class SendMessageModel(BaseModel):
    token: str = Field()
    user: str = Field()
    device: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    message: str = Field()

    def dump(self) -> dict:
        """dumps the content as dictionary without null values

        Returns:
            dict: dictionary dump
        """
        return self.model_dump(exclude_none=True)


if __name__ == "__main__":
    msg = SendMessageModel(token="abc123", user="213", message="hello world!")

    print(msg.dump())
