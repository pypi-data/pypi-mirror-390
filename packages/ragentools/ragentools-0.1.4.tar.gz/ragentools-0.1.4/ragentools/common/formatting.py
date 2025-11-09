from pydantic import BaseModel, create_model
from typing import List, Dict, Any, Type


type_map = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def schema_to_type(schema: Dict[str, Any]) -> Type:
    t = schema["type"]
    if t == "array":
        item_type = schema_to_type(schema["items"])
        return List[item_type]
    return type_map[t]


def get_response_model(response_format: Dict[str, Any]) -> Type[BaseModel]:
    fields = {k: (schema_to_type(v), ...) for k, v in response_format.items()}
    model: Type[BaseModel] = create_model("ResponseModel", **fields)
    return model
