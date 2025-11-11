import numpy as np
from pydantic_core import core_schema
from typing import Any, Annotated


class _NumpyArrayPydanticSchema:
    """
    This is a metadata class that tells Pydantic how to handle
    validation, serialization, and schema generation for NumPy arrays.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        def validate_from_list_or_array(value: Any) -> np.ndarray:
            if isinstance(value, np.ndarray):
                return value
            if isinstance(value, list):
                try:
                    return np.array(value)
                except Exception as e:
                    raise ValueError(f"Could not convert list to numpy array: {e}")
            raise TypeError(f"Expected list or numpy array, got {type(value)}")

        validation_schema = core_schema.no_info_plain_validator_function(validate_from_list_or_array)

        def serialize_to_list(arr: np.ndarray) -> list:
            return arr.tolist()

        serialization_schema = core_schema.plain_serializer_function_ser_schema(
            serialize_to_list, info_arg=False, when_used="json"
        )

        return core_schema.json_or_python_schema(
            json_schema=validation_schema, python_schema=validation_schema, serialization=serialization_schema
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler) -> dict[str, Any]:
        return {"type": "array", "items": {"type": "number"}, "example": [1.0, 2.0, 3.0]}


# --- THIS IS THE TYPE YOU WILL USE ---
# Mypy sees `np.ndarray`.
# Pydantic sees the `_NumpyArrayPydanticSchema` and uses it.
NumpyArray = Annotated[np.ndarray, _NumpyArrayPydanticSchema]
