from typing import List, TypeVar

from pydantic import BaseModel, TypeAdapter

BASE_KURYANA_API_URL = "https://kuryana.tbdh.app/"


T = TypeVar("T", bound=BaseModel)


class BaseClient:
    def _parse_response(self, data: str, class_type: type[T]) -> T:
        return class_type.model_validate_json(data, strict=False)

    def _parse_array_response(
        self, data: str, adapter_type: TypeAdapter[List[T]]
    ) -> List[T]:
        return adapter_type.validate_json(data, strict=False)
