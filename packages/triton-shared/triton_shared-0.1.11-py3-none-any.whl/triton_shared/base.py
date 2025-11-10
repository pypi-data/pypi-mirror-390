from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase for Pydantic aliasing."""
    parts = string.split("_")
    return parts[0] + "".join(p.capitalize() or "_" for p in parts[1:])


class BaseSchema(BaseModel):
    """
    - Internal attribute names: snake_case (Pythonic)
    - External JSON: camelCase via aliases
    - Incoming JSON: accepts camelCase or snake_case (populate_by_name=True)
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
    )
