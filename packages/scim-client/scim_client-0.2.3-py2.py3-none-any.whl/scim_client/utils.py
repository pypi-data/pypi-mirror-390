import re
from typing import Optional, Dict, Any, Callable, List, Union

from scim_client.defaults import Sentinel

EXTENSION_SCHEMA_PREFIX = "urn:ietf:params:scim:schemas:extension"


def _transform_dict_keys(
    d: Union[Dict[str, Any], str, List], transform_fn: Callable[[str], str]
) -> Union[Dict[str, Any], str, List]:
    if isinstance(d, list):
        return [_transform_dict_keys(i, transform_fn) for i in d]
    elif not isinstance(d, dict):
        return d
    return {
        transform_fn(key): _transform_dict_keys(value, transform_fn)
        for key, value in d.items()
    }


def _to_camel_case_key(key: str) -> str:
    parts = key.split("_")
    return parts[0] + "".join([p.title() for p in parts[1:]])


def _to_camel_cased(original: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return _transform_dict_keys(
        original,
        _to_camel_case_key,
    )


def _get_extension_key(key: str) -> str:
    if key.startswith(EXTENSION_SCHEMA_PREFIX):
        key_splits = key.split(":")
        return "".join([key_splits[-3], key_splits[-1]])
    return key


def _to_snake_case_key(key):
    key = _get_extension_key(key)
    return re.sub(
        "^_",
        "",
        "".join(["_" + c.lower() if c.isupper() else c for c in key]),
    )


def _to_snake_cased(original: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return _transform_dict_keys(original, _to_snake_case_key)


def _to_dict_without_not_given(obj: Any) -> dict:
    dict_value = {}
    schema_extension_map = {
        _to_snake_case_key(_get_extension_key(schema)): schema
        for schema in getattr(obj, "schemas", [])
        if schema.startswith(EXTENSION_SCHEMA_PREFIX)
    }
    given_dict = obj if isinstance(obj, dict) else vars(obj)
    for key, value in given_dict.items():
        if key in schema_extension_map:
            key = schema_extension_map[key]
        dict_key = _to_camel_case_key(key)
        if key == "extra_fields":
            continue
        if value is Sentinel:
            continue
        if isinstance(value, list):
            dict_value[dict_key] = [
                elem.to_dict() if hasattr(elem, "to_dict") else elem for elem in value
            ]
        elif isinstance(value, dict):
            dict_value[dict_key] = _to_dict_without_not_given(value)
        else:
            dict_value[dict_key] = (
                value.to_dict() if hasattr(value, "to_dict") else value
            )
    return dict_value
