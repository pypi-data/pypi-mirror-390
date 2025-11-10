from typing import Annotated, Literal
from pydantic import BaseModel, BeforeValidator, Discriminator, Field, Tag


class Mention(BaseModel):
    """Represents a mention

    ```python
    >>> m = Mention(href="http://actor.example/alice", name="@alice@actor.example")
    >>> m.model_dump()
    {'type': 'Mention',
        'href': 'http://actor.example/alice',
        'name': '@alice@actor.example'}

    ```
    """

    type: Literal["Mention"] = Field(default="Mention")
    href: str = Field(
        description="The location the mentioned party can be retrieved at. In the Fediverse usually an actor URI"
    )
    name: str | None = Field(default=None)


class Hashtag(BaseModel):
    """Represents a hashtag

    ```python
    >>> m = Hashtag(name="#cow")
    >>> m.model_dump(exclude_none=True)
    {'type': 'Hashtag', 'name': '#cow'}

    ```
    """

    type: Literal["Hashtag"] = Field(default="Hashtag")
    href: str | None = Field(
        default=None, description="A location related to the hashtag"
    )
    name: str = Field(description="The actual hashtag", examples=["#cow"])


def discriminator_tag(v):
    match v:
        case {"type": "Hashtag"} | Hashtag():
            return "Hashtag"
        case {"type": "Mention"} | Mention():
            return "Mention"
        case dict():
            return "unknown"
        case str():
            return "string"

    raise Exception


def to_link(href: str) -> dict:
    return {"href": href}


TagType = Annotated[
    Annotated[Hashtag, Tag("Hashtag")]
    | Annotated[Mention, Tag("Mention")]
    | Annotated[dict, Tag("unknown")]
    | Annotated[Annotated[dict, BeforeValidator(to_link)], Tag("string")],
    Discriminator(discriminator_tag),
]
