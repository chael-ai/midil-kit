from typing import Generic, TypeVar, Any
from pydantic import BaseModel, Field
from typing import Dict


ItemT = TypeVar("ItemT")


class Page(BaseModel, Generic[ItemT]):
    items: list[ItemT] = Field(..., description="The items of the page")
    size: int = Field(..., description="The size of the page")
    meta: Dict[str, Any] = Field(
        default_factory=dict, description="The meta data of the page"
    )


PageType = TypeVar("PageType", bound=Page[Any])
